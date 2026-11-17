#!/usr/bin/env python3
"""Public news scanner; no credentials or paid API required."""
import json, re, time, os, csv, io, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from balanced_strategy import evaluate_company, THRESHOLDS as BALANCED_THRESHOLDS
from entry_trigger import build_entry_trigger
from early_entry import build_early_entry
from risk_plan import build_risk_plan
from analyst_consensus import load_consensus_csv
from event_risk import load_event_risk_csv
from scenario_valuation import scenario_valuation
from market_symbols import yahoo_symbol, benchmark_for_currency

ROOT=Path(__file__).resolve().parent
UNIVERSE=[
 ('NVDA','NVIDIA','AI chips'),('AVGO','Broadcom','AI infrastructure'),('AMD','Advanced Micro Devices','AI chips'),('TSM','Taiwan Semiconductor','Semiconductors'),('ASML','ASML','Semiconductor equipment'),('ARM','Arm Holdings','Chip architecture'),('MU','Micron Technology','AI memory'),('MRVL','Marvell Technology','AI networking'),('ANET','Arista Networks','AI networking'),('CRDO','Credo Technology','AI networking'),('ALAB','Astera Labs','AI connectivity'),('SMCI','Super Micro Computer','AI servers'),('DELL','Dell Technologies','AI servers'),('VRT','Vertiv','Data centers'),('ETN','Eaton','Data center power'),('GOOGL','Alphabet','AI platforms'),('MSFT','Microsoft','AI platforms'),('AMZN','Amazon','AI cloud'),('META','Meta Platforms','AI platforms'),('PLTR','Palantir','AI software'),('AI','C3.ai','AI software'),('SOUN','SoundHound AI','AI software'),('BBAI','BigBear.ai','AI software'),('PATH','UiPath','Automation'),('NOW','ServiceNow','Enterprise AI'),('SNOW','Snowflake','Data platform'),('PDYN','Palladyne AI','Robotics'),('SYM','Symbotic','Warehouse robotics'),('ISRG','Intuitive Surgical','Surgical robotics'),('TER','Teradyne','Industrial robotics'),('ROK','Rockwell Automation','Industrial automation'),('ABB','ABB Ltd','Industrial automation'),('FANUY','FANUC','Industrial robotics'),('KUKAF','KUKA','Industrial robotics'),('ZBRA','Zebra Technologies','Industrial automation'),('CGNX','Cognex','Machine vision'),('IRBT','iRobot','Consumer robotics'),('SERV','Serve Robotics','Autonomous robots'),('RR','Richtech Robotics','Service robotics'),('JOBY','Joby Aviation','Autonomy'),('ACHR','Archer Aviation','Autonomy'),('MBLY','Mobileye','Autonomous driving'),('LAZR','Luminar Technologies','Autonomous driving'),('OUST','Ouster','Sensors'),('KTOS','Kratos Defense','Autonomous systems'),('RCAT','Red Cat Holdings','Drones'),('ONDS','Ondas Holdings','Drones'),('QCOM','Qualcomm','Edge AI'),('INTC','Intel','Semiconductors'),('APH','Amphenol','AI connectivity'),('GLW','Corning','Optical infrastructure'),('COHR','Coherent','Optical infrastructure'),('LITE','Lumentum','Optical infrastructure'),('CLS','Celestica','AI hardware'),('JBL','Jabil','AI hardware'),('ONTO','Onto Innovation','Semiconductor equipment'),('AMAT','Applied Materials','Semiconductor equipment'),('LRCX','Lam Research','Semiconductor equipment'),('KLAC','KLA Corporation','Semiconductor equipment'),('MPWR','Monolithic Power Systems','Power semiconductors'),('NVT','nVent Electric','Data center power'),('PWR','Quanta Services','Grid infrastructure'),('HUBB','Hubbell','Grid infrastructure'),('EMR','Emerson Electric','Industrial automation'),('HON','Honeywell','Industrial automation'),('SIEGY','Siemens','Industrial automation'),('DHR','Danaher','Laboratory automation'),('AZTA','Azenta','Laboratory automation')]
QUERIES=['artificial intelligence robotics stocks companies contracts earnings', 'AI data center chips networking power infrastructure stocks', 'industrial automation humanoid robots publicly traded companies', 'AI inference optical interconnect semiconductor publicly traded stock', 'warehouse automation machine vision autonomous systems listed company', 'AI infrastructure cooling energy grid power public company']
UA={'User-Agent':'Mozilla/5.0 (compatible; AI-Robotics-Investor/2.0; public research)'}
def fetch(q):
    url='https://news.google.com/rss/search?q='+urllib.parse.quote(q+' when:3d')+'&hl=en-US&gl=US&ceid=US:en'
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=18) as resp: raw=resp.read(600000)
        tree=ET.fromstring(raw)
        result=[]
        for item in tree.findall('.//item')[:35]:
            title=(item.findtext('title') or '').strip(); link=(item.findtext('link') or '').strip(); date=item.findtext('pubDate') or ''
            if title and link: result.append({'title':title,'url':link,'date':date})
        return result
    except Exception as e:
        print('RSS error:',str(e)[:160]); return []
def matches(title,ticker,name):
    t=title.lower()
    # Avoid false matches for very short tickers such as AI, RR, MU
    if len(ticker)>=4 and re.search(r'(?<![a-z0-9])'+re.escape(ticker.lower())+r'(?![a-z0-9])',t): return True
    if name.lower() in t: return True
    aliases={'NVDA':['nvidia'],'AVGO':['broadcom'],'PDYN':['palladyne'],'SYM':['symbotic'],'ISRG':['intuitive surgical'],'TSM':['tsmc'],'GOOGL':['google','alphabet'],'AMZN':['amazon','aws'],'MSFT':['microsoft'],'META':['meta platforms'],'ABB':['abb ltd'],'FANUY':['fanuc'],'MU':['micron'],'AI':['c3.ai'],'RR':['richtech robotics']}
    return any(a in t for a in aliases.get(ticker,[]))

# SEC XBRL financials: official filings, US-reporting issuers only.
# No API key. Bounded requests per scan and persisted cache in scan.json.
SEC_UA=os.environ.get('SEC_USER_AGENT','AI-Robotics-Investor research contact research-team@example.com')
FACTS={
 'revenue':['RevenueFromContractWithCustomerExcludingAssessedTax','Revenues','SalesRevenueNet'],
 'net_income':['NetIncomeLoss'],
 'operating_cash_flow':['NetCashProvidedByUsedInOperatingActivities'],
 'capex':['PaymentsToAcquirePropertyPlantAndEquipment'],
 'assets':['Assets'],
 'liabilities':['Liabilities'],
 'cash':['CashAndCashEquivalentsAtCarryingValue'],
 'debt_current':['LongTermDebtCurrent','LongTermDebtAndCapitalLeaseObligationsCurrent'],
 'debt_long':['LongTermDebtNoncurrent','LongTermDebt'],
 'shares':['CommonStockSharesOutstanding','EntityCommonStockSharesOutstanding'],
}
def sec_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':SEC_UA,'Accept':'application/json','Accept-Encoding':'identity'})
    with urllib.request.urlopen(req,timeout=12) as r: return json.load(r)
def annual_values(facts,tags,unit='USD',instant=False):
    for tag in tags:
        rows=facts.get('us-gaap',{}).get(tag,{}).get('units',{}).get(unit,[])
        rows=[x for x in rows if x.get('form') in ('10-K','20-F') and x.get('fy') and x.get('filed') and x.get('val') is not None and (instant or (x.get('start') and 330<= (datetime.fromisoformat(x['end'])-datetime.fromisoformat(x['start'])).days<=380))]
        if not rows: continue
        byyear={}
        for x in rows:
            year=x['end'][:4]
            if year not in byyear or x['filed']>byyear[year]['filed']: byyear[year]=x
        vals=sorted(byyear.values(),key=lambda x:x['end'],reverse=True)
        if vals:return [{'year':v['end'][:4],'start':v.get('start'),'end':v['end'],'value':v['val'],'filed':v['filed']} for v in vals[:3]]
    return []
def latest_common_end(metrics, *keys):
    """Return newest exact fiscal period shared by every requested flow metric."""
    if not keys or not all(metrics.get(k) for k in keys): return None, None
    common={(x.get('start'),x.get('end')) for x in metrics[keys[0]]}
    for key in keys[1:]: common &= {(x.get('start'),x.get('end')) for x in metrics[key]}
    if not common: return None, None
    start,end=max(common,key=lambda pair:pair[1])
    values={key:next(x['value'] for x in metrics[key] if (x.get('start'),x.get('end'))==(start,end)) for key in keys}
    return {'start':start,'end':end},values

def fundamentals(ticker,cik):
    data=sec_json('https://data.sec.gov/api/xbrl/companyfacts/CIK'+str(cik).zfill(10)+'.json')
    facts=data.get('facts',{}); metrics={}
    for key,tags in FACTS.items():
        metrics[key]=annual_values(facts,tags,'shares' if key=='shares' else 'USD',key in ('assets','liabilities','cash','debt_current','debt_long','shares'))
    # Prefer the latest dated DEI share count, including quarterly filings.
    # The older annual-only us-gaap path remains a fallback.
    if True:
        rows=facts.get('dei',{}).get('EntityCommonStockSharesOutstanding',{}).get('units',{}).get('shares',[])
        rows=[r for r in rows if r.get('form') in ('10-K','10-Q','20-F') and r.get('end') and r.get('filed') and isinstance(r.get('val'),(int,float)) and r['val']>0]
        if rows:
            r=max(rows,key=lambda x:(x['end'],x['filed']))
            dei_share={'year':r['end'][:4],'end':r['end'],'value':r['val'],'filed':r['filed']}
            if not metrics['shares'] or dei_share['end'] >= metrics['shares'][0]['end']:
                metrics['shares']=[dei_share]
    latest=lambda key: metrics[key][0]['value'] if metrics[key] else None
    revenue_period,revenue_pair=latest_common_end(metrics,'revenue','net_income')
    cashflow_period,cashflow_pair=latest_common_end(metrics,'operating_cash_flow','capex')
    rev=latest('revenue'); revenue_latest=metrics['revenue'][0] if metrics['revenue'] else None
    net=revenue_pair.get('net_income') if revenue_pair else None
    ocf=cashflow_pair.get('operating_cash_flow') if cashflow_pair else None
    capex=cashflow_pair.get('capex') if cashflow_pair else None
    margin=round(net/rev*100,1) if rev and net is not None and revenue_period and revenue_latest and (revenue_period['start'],revenue_period['end'])==(revenue_latest.get('start'),revenue_latest.get('end')) else None
    fcf=ocf-abs(capex) if ocf is not None and capex is not None else None
    periods_aligned=bool(revenue_period and cashflow_period and revenue_latest and (revenue_period['start'],revenue_period['end'])==(revenue_latest.get('start'),revenue_latest.get('end')) and revenue_period['end']==metrics['net_income'][0]['end'] and revenue_period['start']==metrics['net_income'][0].get('start') and cashflow_period['end']==metrics['operating_cash_flow'][0]['end']==metrics['capex'][0]['end'] and cashflow_period['start']==metrics['operating_cash_flow'][0].get('start')==metrics['capex'][0].get('start'))
    growth=None
    if len(metrics['revenue'])>1:
        a,b=metrics['revenue'][:2]
        if int(a['year'])-int(b['year'])==1 and b['value']>0:growth=round((a['value']/b['value']-1)*100,1)
    debt=(latest('debt_current') or 0)+(latest('debt_long') or 0) if latest('debt_current') is not None or latest('debt_long') is not None else None
    # This is a data-coverage-aware descriptive score, not a buy recommendation.
    checks=[growth is not None,margin is not None,fcf is not None,ocf is not None]
    score=None
    if all(checks) and periods_aligned:
        score=round(100*(int(growth>15)+int(margin>10)+int(fcf>0)+int(ocf is not None and ocf>0))/4)
    return {'source':'SEC EDGAR XBRL','fiscal_year':metrics['revenue'][0]['year'] if metrics['revenue'] else None,
      'revenue_usd':rev,'net_income_usd':net,'revenue_growth_pct':growth,'net_margin_pct':margin,'operating_cash_flow_usd':ocf,
      'free_cash_flow_usd':fcf,'cash_usd':latest('cash'),'debt_usd':debt,
      'financial_health_score':score,'score_label':'Prosty filtr 4 warunków, nie rekomendacja',
      'shares_outstanding':latest('shares'),'shares_as_of':metrics['shares'][0]['end'] if metrics['shares'] else None,'revenue_period_start':revenue_latest.get('start') if revenue_latest else None,'revenue_period_end':revenue_latest.get('end') if revenue_latest else None,'net_income_period_start':revenue_period.get('start') if revenue_period else None,'net_income_period_end':revenue_period.get('end') if revenue_period else None,'cash_flow_period_start':cashflow_period.get('start') if cashflow_period else None,'cash_flow_period_end':cashflow_period.get('end') if cashflow_period else None,'capex_period_start':cashflow_period.get('start') if cashflow_period else None,'capex_period_end':cashflow_period.get('end') if cashflow_period else None,'period_alignment':{'status':'aligned' if periods_aligned else 'partial_or_mismatched','revenue_net_income':revenue_period,'cash_flow_capex':cashflow_period},'period_mismatch_flags':([] if periods_aligned else ['annual_flow_periods_not_aligned']),'filed':max([x['filed'] for key in ('revenue','net_income','operating_cash_flow','capex') for x in metrics.get(key,[])[:1] if x.get('filed')],default=None),'as_of':datetime.now(timezone.utc).isoformat(),'source_url':'https://www.sec.gov/edgar/browse/?CIK='+str(cik)}
SEC_BATCH_SIZE=16  # max requests per six-hour scan; staggered, no paid API
PRICE_BATCH_SIZE=24  # complete the 68-name rotation in about three successful scans

def add_fundamentals(companies,prior):
    previous={x.get('ticker'):x.get('fundamentals') for x in prior.get('companies',[]) if x.get('fundamentals')}
    try:
        registry=sec_json('https://www.sec.gov/files/company_tickers.json')
        ciks={x['ticker']:x['cik_str'] for x in registry.values() if x.get('ticker')}
    except Exception as e:
        print('SEC issuer registry unavailable:',str(e)[:120]);ciks={}
    # Rotate coverage across scans; cache is retained in data/scan.json.
    # Prioritize uncovered tickers; cap to respect SEC fair-access policies.
    pending=[c for c in companies if c['ticker'] in ciks and (c['ticker'] not in previous or not (previous[c['ticker']] or {}).get('shares_outstanding'))]
    stale=[c for c in companies if c['ticker'] in ciks and c['ticker'] in previous and c not in pending]
    stale.sort(key=lambda c:previous[c['ticker']].get('as_of',''))
    # Canary: refresh AVGO even when cached, then rotate remaining capacity.
    ordered=sorted(pending,key=lambda c:(c['ticker']!='AVGO',c['ticker']))+sorted(stale,key=lambda c:(c['ticker']!='AVGO',previous[c['ticker']].get('as_of','')))
    attempted=0; succeeded=0; refreshed=set()
    for c in ordered[:SEC_BATCH_SIZE]:
        attempted+=1
        try:
            previous[c['ticker']]=fundamentals(c['ticker'],ciks[c['ticker']]);succeeded+=1;refreshed.add(c['ticker']);time.sleep(.35)
        except Exception as e: print('SEC facts',c['ticker'],str(e)[:110])
    print('SEC_BATCH_SUMMARY',json.dumps({'attempted':attempted,'updated':succeeded,'batch_limit':SEC_BATCH_SIZE,'registry_matches':sum(c['ticker'] in ciks for c in companies)}))
    for c in companies:
        c['fundamentals']=previous.get(c['ticker'])
        c['fundamentals_quality']='refreshed' if c['ticker'] in refreshed else ('cached' if previous.get(c['ticker']) else 'unavailable')
        c['valuation_status']='Brak zweryfikowanej bieżącej ceny i kapitalizacji; P/E i EV/FCF niedostępne'
        c['investment_score']=None
    return sum(bool(c['fundamentals']) for c in companies)


# Best-effort EOD quotes. Both sources are unofficial/free and may block access.
# A failed request is NOT a zero price and does not imply a successful price scan.
from datetime import timedelta

class QuoteError(Exception):
    pass

def checked_quote(price, day, source, url):
    try:
        value=float(price)
        stamp=datetime.fromisoformat(str(day)[:10]).date()
    except (ValueError, TypeError, OverflowError) as exc:
        raise QuoteError('invalid price or date') from exc
    age=(datetime.now(timezone.utc).date()-stamp).days
    if not (0 < value < 10000000): raise QuoteError('price out of range')
    if not 0 <= age <= 7: raise QuoteError('stale or future quote: '+str(day))
    return {'close_usd':round(value,4),'date':stamp.isoformat(),'age_days':age,
            'source':source,'source_url':url,'is_live':False}

def stooq_quote(ticker):
    try: symbol=yahoo_symbol(ticker)
    except ValueError as exc: raise QuoteError(str(exc)) from exc
    today=datetime.now(timezone.utc)
    start=(today-timedelta(days=180)).strftime('%Y%m%d')
    url='https://stooq.com/q/d/l/?'+urllib.parse.urlencode({'s':ticker.lower()+'.us','i':'d','d1':start,'d2':today.strftime('%Y%m%d')})
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'text/csv'})
    with urllib.request.urlopen(req,timeout=12) as response:
        body=response.read(60000).decode('utf-8-sig',errors='replace').strip()
    reader=csv.DictReader(io.StringIO(body))
    if not reader.fieldnames or not {'Date','Close','Volume'}.issubset(set(reader.fieldnames)):
        raise QuoteError('Stooq CSV missing Date/Close; header='+repr((reader.fieldnames or [])[:5])+'; preview='+repr(body[:80]))
    rows=list(reader)
    if not rows: raise QuoteError('Stooq CSV has no rows')
    bars=[]
    for row in rows:
        try:
            close=float(row['Close']); volume=float(row['Volume'])
            bar={'date':row['Date'],'close':close,'volume':volume}
            try:
                high=float(row['High']); low=float(row['Low'])
                if high>=low>0: bar.update(high=high,low=low)
            except (KeyError,TypeError,ValueError): pass
            if close>0 and volume>=0: bars.append(bar)
        except (TypeError,ValueError): continue
    quote=checked_quote(rows[-1].get('Close'),rows[-1].get('Date'),'Stooq EOD',url)
    quote['currency']='USD'
    quote['market_symbol']=ticker
    quote['bars']=bars
    return quote

def yahoo_quote(ticker):
    # Public chart endpoint: availability and redistribution rights may change.
    try: symbol=yahoo_symbol(ticker)
    except ValueError as exc: raise QuoteError(str(exc)) from exc
    url='https://query1.finance.yahoo.com/v8/finance/chart/'+urllib.parse.quote(symbol)+'?interval=1d&range=6mo'
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=12) as response:
        obj=json.load(response)
    results=(obj.get('chart') or {}).get('result') or []
    if not results: raise QuoteError('Yahoo chart has no result')
    result=results[0]
    meta=result.get('meta') or {}
    currency=(meta.get('currency') or '').upper()
    if not re.fullmatch(r'[A-Z]{3}',currency): raise QuoteError('Yahoo quote currency missing or invalid')
    stamps=result.get('timestamp') or []
    quote_rows=((result.get('indicators') or {}).get('quote') or [{}])[0]
    closes=quote_rows.get('close') or []; volumes=quote_rows.get('volume') or []
    highs=quote_rows.get('high') or []; lows=quote_rows.get('low') or []
    valid=[(ts,close) for ts,close in zip(stamps,closes) if close is not None]
    if not valid: raise QuoteError('Yahoo chart has no daily closes')
    ts,price=valid[-1]
    day=datetime.fromtimestamp(ts,timezone.utc).date().isoformat()
    quote=checked_quote(price,day,'Yahoo Finance chart EOD',url)
    quote['currency']=currency
    quote['market_symbol']=symbol
    quote['bars']=[]
    for i,(t,v) in enumerate(zip(stamps,closes)):
        if v is None: continue
        bar={'date':datetime.fromtimestamp(t,timezone.utc).date().isoformat(),'close':float(v),'volume':float(volumes[i] or 0) if i<len(volumes) else 0.0}
        if i<len(highs) and i<len(lows) and highs[i] is not None and lows[i] is not None:
            try:
                high=float(highs[i]); low=float(lows[i])
                if high>=low>0: bar.update(high=high,low=low)
            except (TypeError,ValueError): pass
        quote['bars'].append(bar)
    return quote

def _market_symbol_supported(ticker):
    try: yahoo_symbol(ticker); return True
    except ValueError: return False

def add_prices(companies,prior):
    old={x.get('ticker'):x.get('price') for x in prior.get('companies',[]) if x.get('price')}
    diagnostics={};attempted=0;success=0
    eligible=[c for c in companies if _market_symbol_supported(c['ticker'])]
    # Always check AVGO as a canary; rotate remaining slots across scans.
    eligible.sort(key=lambda c:(c['ticker']!='AVGO',bool(old.get(c['ticker'],{}).get('close_usd')),old.get(c['ticker'],{}).get('checked_at',''),c['ticker']))
    for c in eligible[:PRICE_BATCH_SIZE]:
        ticker=c['ticker'];attempted+=1;errors=[]
        for name,provider in ([('Stooq',stooq_quote),('Yahoo',yahoo_quote)] if re.fullmatch(r'[A-Z]{1,5}',ticker) else [('Yahoo',yahoo_quote)]):
            try:
                quote=provider(ticker)
                quote['checked_at']=datetime.now(timezone.utc).isoformat()
                old[ticker]=quote;success+=1
                diagnostics[ticker]={'status':'ok','provider':name,'date':quote['date']}
                break
            except Exception as exc:
                errors.append(name+': '+str(exc)[:160])
        else:
            diagnostics[ticker]={'status':'failed','errors':errors}
            print('QUOTE_FAIL',ticker,' | '.join(errors))
        time.sleep(.1)
    for c in companies:
        q=old.get(c['ticker'])
        if q:
            try:
                age=(datetime.now(timezone.utc).date()-datetime.fromisoformat(q['date']).date()).days
                if not 0<=age<=7:q=None
            except (ValueError,KeyError,TypeError):q=None
        c['price']=q
        if q and q.get('currency')!='USD':
            c['price']['native_close']=c['price'].get('close_usd')
            c['price']['native_currency']=q.get('currency')
            c['price']['close_usd']=None
        try:
            refreshed=(datetime.now(timezone.utc)-datetime.fromisoformat(q['checked_at'])).total_seconds()<=900 if q and q.get('checked_at') else False
        except (ValueError,TypeError): refreshed=False
        c['price_quality']='refreshed' if refreshed and q.get('date') else ('cached' if q else 'unavailable')
    coverage=sum(bool(c['price']) for c in companies)
    status='ok' if success==attempted and attempted else ('partial' if success else 'unavailable')
    print('PRICE_SUMMARY',json.dumps({'attempted':attempted,'updated':success,'coverage':coverage,'status':status,'batch_limit':PRICE_BATCH_SIZE}))
    return coverage,{'status':status,'attempted':attempted,'updated':success,'coverage':coverage,'diagnostics':diagnostics}

def technical_indicators(quote, benchmark_quote=None):
    """Compute indicators only from validated daily bars, without synthetic values."""
    rows=[]
    for bar in quote.get('bars') or []:
        try:
            day=datetime.fromisoformat(bar['date']).date()
            close=float(bar['close']); volume=float(bar['volume'])
            if close>0 and volume>=0: rows.append((day,close,volume))
        except (KeyError,TypeError,ValueError,OverflowError): continue
    rows.sort(key=lambda x:x[0])
    if len(rows)<50: return {'status':'incomplete','bars':len(rows),'reason':'minimum_50_daily_bars_required'}
    closes=[x[1] for x in rows]; volumes=[x[2] for x in rows]; day=rows[-1][0].isoformat()
    sma20=sum(closes[-20:])/20; sma50=sum(closes[-50:])/50
    changes=[closes[i]-closes[i-1] for i in range(1,len(closes))]
    # Wilder RSI(14): seed with the first 14 changes, then apply recursive smoothing.
    seed=changes[:14]
    ag=sum(max(x,0) for x in seed)/14
    al=sum(max(-x,0) for x in seed)/14
    for change in changes[14:]:
        ag=(ag*13+max(change,0))/14
        al=(al*13+max(-change,0))/14
    rsi=100.0 if al==0 else (0.0 if ag==0 else 100-100/(1+ag/al))
    avg_volume=sum(volumes[-20:])/20
    # Wilder ATR(14) requires genuine daily high/low/previous-close observations.
    atr=None; support20=None; resistance20=None
    if len(rows)>=21 and all('high' in b and 'low' in b for b in (quote.get('bars') or [])[-21:]):
        raw={}
        for b in quote.get('bars') or []:
            try: raw[datetime.fromisoformat(b['date']).date()]=(float(b['high']),float(b['low']))
            except (KeyError,TypeError,ValueError): continue
        aligned=[(d,raw[d][0],raw[d][1],closes[i]) for i,(d,_,_) in enumerate(rows) if d in raw]
        if len(aligned)>=15:
            tr=[]
            for i,(d,high,low,close) in enumerate(aligned):
                if i==0: continue
                prev=aligned[i-1][3]
                tr.append(max(high-low,abs(high-prev),abs(low-prev)))
            if len(tr)>=14:
                atr=sum(tr[:14])/14
                for value in tr[14:]: atr=(atr*13+value)/14
                atr=round(atr,6)
            last20=aligned[-20:]
            if len(last20)==20:
                support20=round(min(x[2] for x in last20),6)
                resistance20=round(max(x[1] for x in last20),6)
    rs=None
    benchmark=benchmark_quote.get('market_symbol','SPY') if benchmark_quote else 'SPY'
    bench_rows={}
    for bar in (benchmark_quote or {}).get('bars') or []:
        try: bench_rows[datetime.fromisoformat(bar['date']).date()]=float(bar['close'])
        except (KeyError,TypeError,ValueError): continue
    common=[(d,closes[i]) for i,(d,_,_) in enumerate(rows) if d in bench_rows and bench_rows[d]>0]
    if len(common)>=21:
        rs=((common[-1][1]/common[-21][1])/(bench_rows[common[-1][0]]/bench_rows[common[-21][0]])-1)*100
    return {'status':'ok','bars':len(rows),'date':day,'sma20':sma20,'sma50':sma50,
      'rsi_14':round(rsi,2),'volume_ratio20':round(volumes[-1]/avg_volume,3) if avg_volume else None,
      'above_sma20':closes[-1]>sma20,'above_sma50':closes[-1]>sma50,
      'relative_strength_20d_pct':round(rs,2) if rs is not None else None,'relative_strength_benchmark':benchmark if rs is not None else None,
      'atr_14':atr,'support_20d':support20,'resistance_20d':resistance20,
      'atr_status':'ok' if atr is not None else 'unavailable_high_low_missing',
      'method':'SMA20/SMA50, Wilder RSI14, Wilder ATR14 from genuine high/low bars; 20-session relative performance versus SPY on common dates'}

def calculate_valuation(company, today=None):
    """Indicative trailing annual ratios, only if SEC periods and shares are defensible.

    This is NOT a live valuation or an investment recommendation. No estimated shares.
    """
    today=today or datetime.now(timezone.utc).date()
    f=company.get('fundamentals') or {}; q=company.get('price') or {}
    result={'status':'unavailable','reason':'Brak ceny lub kompletnych danych SEC','market_cap_usd':None,
            'ps':None,'pe':None,'fcf_yield_pct':None,'share_date':f.get('shares_as_of'),
            'price_date':q.get('date'),'basis':'Roczne raporty SEC + ostatnia cena zamknięcia (przybliżenie)'}
    try:
        price=float(q['close_usd']); shares=float(f['shares_outstanding'])
        if q.get('currency','USD')!='USD': raise ValueError('non-USD quote requires verified FX conversion')
        if not (0<price<1e7 and 0<shares<1e13): raise ValueError('invalid price/shares')
        share_day=datetime.fromisoformat(f['shares_as_of']).date()
        quote_day=datetime.fromisoformat(q['date']).date()
        if not 0 <= (today-share_day).days <= 540: raise ValueError('stale share count')
        if not 0 <= (today-quote_day).days <= 7: raise ValueError('stale quote')
        # SEC shares for foreign ADRs may refer to underlying ordinary shares, not US ADRs.
        if '.' in company.get('ticker','') or company.get('ticker') in {'TSM','ASML','ARM','ABB','FANUY','SIEGY'}:
            raise ValueError('ADR/foreign share-unit ambiguity')
        cap=price*shares
        result['market_cap_usd']=round(cap)
        result['status']='partial';result['reason']='Kapitalizacja orientacyjna; liczba akcji z historycznego raportu SEC'
        def period_ok(key):
            day=f.get(key)
            if not day:return False
            d=datetime.fromisoformat(day).date()
            return 0 <= (today-d).days <= 540
        revenue=f.get('revenue_usd')
        if period_ok('revenue_period_end') and isinstance(revenue,(int,float)) and revenue>0:
            result['ps']=round(cap/revenue,2)
        net=f.get('net_income_usd')
        if (period_ok('net_income_period_end') and f.get('net_income_period_end')==f.get('revenue_period_end') and f.get('net_income_period_start') and f.get('net_income_period_start')==f.get('revenue_period_start') and isinstance(net,(int,float)) and net>0):
            result['pe']=round(cap/net,2)
        fcf=f.get('free_cash_flow_usd')
        if (period_ok('cash_flow_period_end') and period_ok('capex_period_end')
            and f.get('cash_flow_period_end')==f.get('capex_period_end')
            and f.get('cash_flow_period_start') and f.get('capex_period_start')
            and f.get('cash_flow_period_start')==f.get('capex_period_start')
            and isinstance(fcf,(int,float))):
            result['fcf_yield_pct']=round(100*fcf/cap,2)
        return result
    except (ValueError,KeyError,TypeError,OverflowError) as exc:
        result['reason']=str(exc) if str(exc) else 'Brak ceny lub liczby akcji'
        return result

def summarize_signals(companies):
    """Counts decision states without changing or promoting any signal."""
    return {
        'buy':sum(1 for c in companies if c.get('investment_decision',{}).get('signal')=='BUY' and c.get('buy_eligible') is True),
        'early_entry_watch':sum(1 for c in companies if c.get('early_buy_watch') is True),
        'active_technical_trigger':sum(1 for c in companies if c.get('entry_trigger',{}).get('active') is True),
        'watch':sum(1 for c in companies if c.get('signal','WATCH')=='WATCH'),
        'blocked':sum(1 for c in companies if c.get('investment_decision',{}).get('buy_eligible') is not True),
    }

def main():
    allnews=[]; seen=set()
    for q in QUERIES:
        for n in fetch(q):
            if n['url'] not in seen: seen.add(n['url']); allnews.append(n)
        time.sleep(.3)
    companies=[]
    for ticker,name,sector in UNIVERSE:
        hits=[n for n in allnews if matches(n['title'],ticker,name)]
        companies.append({'ticker':ticker,'name':name,'sector':sector,'mentions':len(hits),'news':hits[:5], 'status':'Do analizy' if hits else 'Obserwacja'})
    companies.sort(key=lambda x:(-x['mentions'],x['ticker']))
    # Discovery is evidence-based: new tickers are proposed from public SEC issuer list,
    # but only when company names appear in actual fetched headlines.
    # This is a US SEC coverage extension, NOT a complete global equity screener.
    discoveries=[]
    try:
        req=urllib.request.Request('https://www.sec.gov/files/company_tickers.json',headers={'User-Agent':'AI Robotics Investor research contact investor-research@example.org','Accept':'application/json'})
        with urllib.request.urlopen(req,timeout=18) as resp: registry=json.load(resp)
        existing={t for t,_,_ in UNIVERSE}
        keywords=('robot','automat','semiconductor','photon','laser','vision','aerospace','intelligent','artificial intelligence','computing','data center','technology','technologies','systems','networks','electronic','software')
        blacklist={'international business machines','general electric','apple','amazon','alphabet','microsoft','meta platforms'}
        for record in registry.values():
            ticker=record.get('ticker',''); name=record.get('title','').strip()
            if ticker in existing or not (5<=len(name)<=65) or not any(k in name.lower() for k in keywords) or name.lower() in blacklist: continue
            # Full-name phrase only: avoid spurious matches for short tickers.
            hits=[n for n in allnews if name.lower() in n['title'].lower()]
            if hits:
                discoveries.append({'ticker':ticker,'name':name,'mentions':len(hits),'news':hits[:3],'public_listing':'SEC ticker registry (US); ticker requires verification','evidence':'Exact issuer name in collected headline'})
        discoveries=sorted(discoveries,key=lambda x:(-x['mentions'],x['ticker']))[:35]
    except Exception as e:
        print('SEC registry unavailable:',str(e)[:120])
    # Attention score measures recent source coverage, never undervaluation or upside.
    for c in companies:
        c['attention_score']=min(100,round(100*(1-2.718281828**(-c['mentions']/4))))
        c['valuation_status']='Brak zweryfikowanych danych o wycenie'
        c['investment_score']=None
    for c in discoveries:
        c['attention_score']=min(100,round(100*(1-2.718281828**(-c['mentions']/4))))
        c['investment_score']=None
    try:
        prior=json.loads((ROOT/'data'/'scan.json').read_text(encoding='utf-8'))
    except Exception: prior={}
    covered=add_fundamentals(companies,prior)
    price_coverage,price_health=add_prices(companies,prior)
    for c in companies:
        c['valuation']=calculate_valuation(c)
        c['valuation_status']=('Orientacyjna kapitalizacja i mnożniki roczne — nie ranking zakupu' if c['valuation']['status']=='partial' else 'Brak wystarczających danych do wyceny')
    valuation_coverage=sum(c['valuation']['status']=='partial' for c in companies)
    # Fetch a separate broad-market benchmark; relative strength stays unavailable if it fails.
    try: benchmark_quote=yahoo_quote('SPY')
    except Exception as exc:
        benchmark_quote={}; print('BENCHMARK_FAIL SPY',str(exc)[:180])
    # External analyst/event feeds are opt-in CSV inputs with strict provenance and freshness checks.
    consensus_by_ticker=load_consensus_csv(ROOT/'data'/'analyst_consensus.csv')
    event_feed=load_event_risk_csv(ROOT/'data'/'corporate_events.csv')
    # Evaluate every security; absent feeds remain explicit blockers.
    for company in companies:
        # Relative strength is only comparable to SPY for USD-denominated listings.
        quote=company.get('price') or {}
        comparable_benchmark=benchmark_quote if quote.get('currency','USD')=='USD' else None
        tech=technical_indicators(quote,comparable_benchmark)
        company['technical']=tech
        q=company.get('price') or {}
        if tech.get('status')=='ok':
            q.update({k:tech.get(k) for k in ('sma20','sma50','rsi_14','volume_ratio20','above_sma20','above_sma50','relative_strength_20d_pct','relative_strength_benchmark')})
            q['rsi_as_of']=q['date']; q['sma20_as_of']=q['date']; q['sma50_as_of']=q['date']; q['volume_as_of']=q['date']
        company['analyst_targets']=consensus_by_ticker.get(company['ticker'],{'status':'unavailable','reason':'no validated point-in-time analyst_consensus.csv row'})
        company['entry_trigger']=build_entry_trigger(company)
        company['early_entry']=build_early_entry(company)
        company['early_buy_watch']=bool(company['early_entry'].get('near_entry'))
        company['risk_plan']=build_risk_plan(company)
        event_flags=list(event_feed.get('flags') or [])
        matching_events=[e for e in event_feed.get('events',[]) if e.get('ticker','').upper()==company['ticker']]
        if matching_events: event_flags.append('critical_event_within_horizon')
        company['corporate_events']=matching_events
        company['investment_risk_flags']={'flags':sorted(set(event_flags))}
        valuation=company.get('valuation') or {}
        valuation['periods_aligned']=bool((company.get('fundamentals') or {}).get('period_alignment',{}).get('status')=='aligned')
        company['valuation']=valuation
        decision=evaluate_company(company)
        company['investment_decision']=decision
        company['signal']=decision.get('signal','WATCH')
        company['investment_score']=decision.get('fundamental_score')
        company['buy_eligible']=bool(decision.get('buy_eligible'))
    missing={}
    for c in companies:
        if c['valuation']['status']=='partial': continue
        f=c.get('fundamentals') or {}
        q=c.get('price') or {}
        reasons=[]
        if not q.get('close_usd'): reasons.append('price_or_verified_fx')
        if not f: reasons.append('SEC_facts')
        elif not f.get('shares_outstanding'): reasons.append('shares')
        elif not f.get('shares_as_of'): reasons.append('shares_date')
        if c['valuation'].get('reason') not in ('Brak ceny lub kompletnych danych SEC',None):reasons.append(c['valuation']['reason'])
        for r in reasons:missing[r]=missing.get(r,0)+1
        if c['ticker']=='AVGO': print('VALUATION_AVGO',json.dumps({'price':bool(q.get('close_usd')),'shares':bool(f.get('shares_outstanding')),'share_date':f.get('shares_as_of'),'reason':c['valuation']['reason'],'status':c['valuation']['status']}))
    print('VALUATION_SUMMARY',json.dumps({'covered':valuation_coverage,'total':len(companies),'missing':missing}))
    signal_summary=summarize_signals(companies)
    payload={'signal_summary':signal_summary,'generated_at':datetime.now(timezone.utc).isoformat(),'source':'Google News RSS','queries':QUERIES,'scan_status':'ok' if allnews else 'no_sources', 'articles_collected':len(allnews),'companies':companies,'discoveries':discoveries,'articles':allnews[:100],'version':'4.2.2','valuation_coverage':valuation_coverage,'valuation_note':'Orientacyjna kapitalizacja = cena EOD × akcje z ostatniego dostępnego raportu SEC; nie uwzględnia późniejszego rozwodnienia, zmian liczby akcji ani ADR. P/S i P/E bazują na danych rocznych, nie TTM. Nie jest to ranking inwestycyjny.','price_health':price_health,'price_coverage':price_coverage,'price_note':'Opóźnione ceny dzienne z Stooq lub Yahoo Chart (źródła mogą blokować dostęp); daty do 7 dni. Brak ceny to brak danych, nie zero. Kapitalizacja i mnożniki wyłącznie orientacyjne, gdy dane są wystarczające.','financial_coverage':covered,'financial_source':'SEC EDGAR XBRL, annual 10-K/20-F where available','financial_limitations':'Dane historyczne, możliwe opóźnienia; nie wszystkie spółki raportują do SEC. Pokrycie rośnie stopniowo; limity 16 zapytań SEC i 24 prób cen na skan.','coverage_note':'Lista startowa plus kandydaci wykryci przez dopasowanie nazw do rejestru SEC; brak pełnego globalnego pokrycia','ranking_method':'attention_score = 100*(1-exp(-mentions/4)); wskaźnik uwagi, NIE ocena inwestycyjna','investment_ranking_available':False,'investment_ranking_status':'BLOCKED_INCOMPLETE_DATA_AND_NO_VALIDATED_BACKTEST','strategy_version':BALANCED_THRESHOLDS,'disclaimer':'Wskaźnik uwagi nie oznacza atrakcyjnej wyceny, potencjału wzrostu ani rekomendacji. Rejestr SEC obejmuje głównie emitentów raportujących w USA. Dane RSS mogą być niepełne.'}
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'data'/'scan.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Scanned',len(companies),'companies,',len(allnews),'articles')
if __name__=='__main__': main()
