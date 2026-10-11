#!/usr/bin/env python3
"""Public news scanner; no credentials or paid API required."""
import json, re, time, os, csv, io, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

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
 'shares':['CommonStockSharesOutstanding'],
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
        if vals:return [{'year':v['end'][:4],'end':v['end'],'value':v['val'],'filed':v['filed']} for v in vals[:3]]
    return []
def fundamentals(ticker,cik):
    data=sec_json('https://data.sec.gov/api/xbrl/companyfacts/CIK'+str(cik).zfill(10)+'.json')
    facts=data.get('facts',{}); metrics={}
    for key,tags in FACTS.items():
        metrics[key]=annual_values(facts,tags,'shares' if key=='shares' else 'USD',key in ('assets','liabilities','cash','debt_current','debt_long','shares'))
    latest=lambda key: metrics[key][0]['value'] if metrics[key] else None
    rev=latest('revenue'); net=latest('net_income'); ocf=latest('operating_cash_flow'); capex=latest('capex')
    margin=round(net/rev*100,1) if rev and net is not None else None
    fcf=ocf-abs(capex) if ocf is not None and capex is not None else None
    growth=None
    if len(metrics['revenue'])>1:
        a,b=metrics['revenue'][:2]
        if int(a['year'])-int(b['year'])==1 and b['value']>0:growth=round((a['value']/b['value']-1)*100,1)
    debt=(latest('debt_current') or 0)+(latest('debt_long') or 0) if latest('debt_current') is not None or latest('debt_long') is not None else None
    # This is a data-coverage-aware descriptive score, not a buy recommendation.
    checks=[growth is not None,margin is not None,fcf is not None]
    score=None
    if all(checks):
        score=round(100*(int(growth>15)+int(margin>10)+int(fcf>0)+int(ocf is not None and ocf>0))/4)
    return {'source':'SEC EDGAR XBRL','fiscal_year':metrics['revenue'][0]['year'] if metrics['revenue'] else None,
      'revenue_usd':rev,'revenue_growth_pct':growth,'net_margin_pct':margin,'operating_cash_flow_usd':ocf,
      'free_cash_flow_usd':fcf,'cash_usd':latest('cash'),'debt_usd':debt,
      'financial_health_score':score,'score_label':'Prosty filtr 4 warunków, nie rekomendacja',
      'as_of':datetime.now(timezone.utc).isoformat(),'source_url':'https://www.sec.gov/edgar/browse/?CIK='+str(cik)}
def add_fundamentals(companies,prior):
    previous={x.get('ticker'):x.get('fundamentals') for x in prior.get('companies',[]) if x.get('fundamentals')}
    try:
        registry=sec_json('https://www.sec.gov/files/company_tickers.json')
        ciks={x['ticker']:x['cik_str'] for x in registry.values() if x.get('ticker')}
    except Exception as e:
        print('SEC issuer registry unavailable:',str(e)[:120]);ciks={}
    # Rotate coverage across scans; cache is retained in data/scan.json.
    # Prioritize uncovered tickers; cap to respect SEC fair-access policies.
    pending=[c for c in companies if c['ticker'] in ciks and c['ticker'] not in previous]
    stale=[c for c in companies if c['ticker'] in ciks and c['ticker'] in previous]
    stale.sort(key=lambda c:previous[c['ticker']].get('as_of',''))
    for c in (pending+stale)[:8]:
        try:
            previous[c['ticker']]=fundamentals(c['ticker'],ciks[c['ticker']]);time.sleep(.25)
        except Exception as e: print('SEC facts',c['ticker'],str(e)[:110])
    for c in companies:
        c['fundamentals']=previous.get(c['ticker'])
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
    if not re.fullmatch(r'[A-Z]{1,5}',ticker): raise QuoteError('unsupported ticker')
    today=datetime.now(timezone.utc)
    start=(today-timedelta(days=14)).strftime('%Y%m%d')
    url='https://stooq.com/q/d/l/?'+urllib.parse.urlencode({'s':ticker.lower()+'.us','i':'d','d1':start,'d2':today.strftime('%Y%m%d')})
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'text/csv'})
    with urllib.request.urlopen(req,timeout=12) as response:
        body=response.read(60000).decode('utf-8-sig',errors='replace').strip()
    reader=csv.DictReader(io.StringIO(body))
    if not reader.fieldnames or not {'Date','Close'}.issubset(set(reader.fieldnames)):
        raise QuoteError('Stooq CSV missing Date/Close; header='+repr((reader.fieldnames or [])[:5])+'; preview='+repr(body[:80]))
    rows=list(reader)
    if not rows: raise QuoteError('Stooq CSV has no rows')
    return checked_quote(rows[-1].get('Close'),rows[-1].get('Date'),'Stooq EOD',url)

def yahoo_quote(ticker):
    # Public chart endpoint: availability and redistribution rights may change.
    if not re.fullmatch(r'[A-Z]{1,5}',ticker): raise QuoteError('unsupported ticker')
    url='https://query1.finance.yahoo.com/v8/finance/chart/'+urllib.parse.quote(ticker)+'?interval=1d&range=15d'
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=12) as response:
        obj=json.load(response)
    results=(obj.get('chart') or {}).get('result') or []
    if not results: raise QuoteError('Yahoo chart has no result')
    result=results[0]
    meta=result.get('meta') or {}
    if meta.get('currency')!='USD': raise QuoteError('Yahoo quote currency is not USD')
    stamps=result.get('timestamp') or []
    closes=(((result.get('indicators') or {}).get('quote') or [{}])[0].get('close') or [])
    valid=[(ts,close) for ts,close in zip(stamps,closes) if close is not None]
    if not valid: raise QuoteError('Yahoo chart has no daily closes')
    ts,price=valid[-1]
    day=datetime.fromtimestamp(ts,timezone.utc).date().isoformat()
    return checked_quote(price,day,'Yahoo Finance chart EOD',url)

def add_prices(companies,prior):
    old={x.get('ticker'):x.get('price') for x in prior.get('companies',[]) if x.get('price')}
    diagnostics={};attempted=0;success=0
    eligible=[c for c in companies if re.fullmatch(r'[A-Z]{1,5}',c['ticker'])]
    # Always check AVGO as a canary; rotate remaining slots across scans.
    eligible.sort(key=lambda c:(c['ticker']!='AVGO',old.get(c['ticker'],{}).get('checked_at',''),c['ticker']))
    for c in eligible[:12]:
        ticker=c['ticker'];attempted+=1;errors=[]
        for name,provider in [('Stooq',stooq_quote),('Yahoo',yahoo_quote)]:
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
    coverage=sum(bool(c['price']) for c in companies)
    status='ok' if success==attempted and attempted else ('partial' if success else 'unavailable')
    print('PRICE_SUMMARY',json.dumps({'attempted':attempted,'updated':success,'coverage':coverage,'status':status}))
    return coverage,{'status':status,'attempted':attempted,'updated':success,'coverage':coverage,'diagnostics':diagnostics}

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
    payload={'generated_at':datetime.now(timezone.utc).isoformat(),'source':'Google News RSS','queries':QUERIES,'scan_status':'ok' if allnews else 'no_sources', 'articles_collected':len(allnews),'companies':companies,'discoveries':discoveries,'articles':allnews[:100],'version':'4.1.1','price_health':price_health,'price_coverage':price_coverage,'price_note':'Opóźnione ceny dzienne z Stooq lub Yahoo Chart (źródła mogą blokować dostęp); daty do 7 dni. Brak ceny to brak danych, nie zero. Bez kapitalizacji i wiarygodnej wyceny.','financial_coverage':covered,'financial_source':'SEC EDGAR XBRL, annual 10-K/20-F where available','financial_limitations':'Dane historyczne, możliwe opóźnienia; brak cen i pełnej wyceny; nie wszystkie spółki raportują do SEC','coverage_note':'Lista startowa plus kandydaci wykryci przez dopasowanie nazw do rejestru SEC; brak pełnego globalnego pokrycia','ranking_method':'attention_score = 100*(1-exp(-mentions/4)); wskaźnik uwagi, NIE ocena inwestycyjna','investment_ranking_available':False,'disclaimer':'Wskaźnik uwagi nie oznacza atrakcyjnej wyceny, potencjału wzrostu ani rekomendacji. Rejestr SEC obejmuje głównie emitentów raportujących w USA. Dane RSS mogą być niepełne.'}
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'data'/'scan.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Scanned',len(companies),'companies,',len(allnews),'articles')
if __name__=='__main__': main()
