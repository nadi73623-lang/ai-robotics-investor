#!/usr/bin/env python3
"""Public news scanner; no credentials or paid API required."""
import json, re, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent
UNIVERSE=[
 ('NVDA','NVIDIA','AI chips'),('AVGO','Broadcom','AI infrastructure'),('AMD','Advanced Micro Devices','AI chips'),('TSM','Taiwan Semiconductor','Semiconductors'),('ASML','ASML','Semiconductor equipment'),('ARM','Arm Holdings','Chip architecture'),('MU','Micron Technology','AI memory'),('MRVL','Marvell Technology','AI networking'),('ANET','Arista Networks','AI networking'),('CRDO','Credo Technology','AI networking'),('ALAB','Astera Labs','AI connectivity'),('SMCI','Super Micro Computer','AI servers'),('DELL','Dell Technologies','AI servers'),('VRT','Vertiv','Data centers'),('ETN','Eaton','Data center power'),('GOOGL','Alphabet','AI platforms'),('MSFT','Microsoft','AI platforms'),('AMZN','Amazon','AI cloud'),('META','Meta Platforms','AI platforms'),('PLTR','Palantir','AI software'),('AI','C3.ai','AI software'),('SOUN','SoundHound AI','AI software'),('BBAI','BigBear.ai','AI software'),('PATH','UiPath','Automation'),('NOW','ServiceNow','Enterprise AI'),('SNOW','Snowflake','Data platform'),('PDYN','Palladyne AI','Robotics'),('SYM','Symbotic','Warehouse robotics'),('ISRG','Intuitive Surgical','Surgical robotics'),('TER','Teradyne','Industrial robotics'),('ROK','Rockwell Automation','Industrial automation'),('ABB','ABB Ltd','Industrial automation'),('FANUY','FANUC','Industrial robotics'),('KUKAF','KUKA','Industrial robotics'),('ZBRA','Zebra Technologies','Industrial automation'),('CGNX','Cognex','Machine vision'),('IRBT','iRobot','Consumer robotics'),('SERV','Serve Robotics','Autonomous robots'),('RR','Richtech Robotics','Service robotics'),('JOBY','Joby Aviation','Autonomy'),('ACHR','Archer Aviation','Autonomy'),('MBLY','Mobileye','Autonomous driving'),('LAZR','Luminar Technologies','Autonomous driving'),('OUST','Ouster','Sensors'),('KTOS','Kratos Defense','Autonomous systems'),('RCAT','Red Cat Holdings','Drones'),('ONDS','Ondas Holdings','Drones'),('QCOM','Qualcomm','Edge AI'),('INTC','Intel','Semiconductors')]
QUERIES=['artificial intelligence robotics stocks companies contracts earnings', 'AI data center chips networking power infrastructure stocks', 'industrial automation humanoid robots publicly traded companies']
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
    # Explicitly surface discovered names not in seed universe for human validation
    candidate_names=['Figure AI','Agility Robotics','Apptronik','1X Technologies','Skild AI','Physical Intelligence','Neura Robotics','Sanctuary AI','Covariant','Unitree','Boston Dynamics','Hugging Face']
    discoveries=[{'name':name,'mentions':sum(name.lower() in n['title'].lower() for n in allnews),'public_listing':'Niezweryfikowany / możliwa spółka prywatna'} for name in candidate_names]
    discoveries=[x for x in discoveries if x['mentions']>0]
    payload={'generated_at':datetime.now(timezone.utc).isoformat(),'source':'Google News RSS','queries':QUERIES,'scan_status':'ok' if allnews else 'no_sources', 'articles_collected':len(allnews),'companies':companies,'discoveries':discoveries,'articles':allnews[:70],'disclaimer':'Liczba wzmianek NIE oznacza potencjału wzrostu ani rekomendacji. Źródła RSS mogą być opóźnione lub niedostępne. Lista nie obejmuje całej giełdy.'}
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'data'/'scan.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Scanned',len(companies),'companies,',len(allnews),'articles')
if __name__=='__main__': main()
