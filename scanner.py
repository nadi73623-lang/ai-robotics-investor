#!/usr/bin/env python3
"""Public news scanner; no credentials or paid API required."""
import json, re, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
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
    payload={'generated_at':datetime.now(timezone.utc).isoformat(),'source':'Google News RSS','queries':QUERIES,'scan_status':'ok' if allnews else 'no_sources', 'articles_collected':len(allnews),'companies':companies,'discoveries':discoveries,'articles':allnews[:100],'version':'3.0','coverage_note':'Lista startowa plus kandydaci wykryci przez dopasowanie nazw do rejestru SEC; brak pełnego globalnego pokrycia','ranking_method':'attention_score = 100*(1-exp(-mentions/4)); wskaźnik uwagi, NIE ocena inwestycyjna','investment_ranking_available':False,'disclaimer':'Wskaźnik uwagi nie oznacza atrakcyjnej wyceny, potencjału wzrostu ani rekomendacji. Rejestr SEC obejmuje głównie emitentów raportujących w USA. Dane RSS mogą być niepełne.'}
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'data'/'scan.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Scanned',len(companies),'companies,',len(allnews),'articles')
if __name__=='__main__': main()
