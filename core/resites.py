import httplib
import urllib2
import re
import random
from xml.dom import minidom
from BeautifulSoup import BeautifulSoup
import logging
from google.appengine.ext import db
#-------------------- TEMPLATE --------------------------
# offers = []
# offers = [['link1','img1','desc1','price1'],['link2','img2','desc2','price2']]


#--------------- GLOBAL VARIABLES -----------------------

TBQURBANO = "http://www.tambaquiurbano.com" 
GPN ="http://api.groupon.de/feed/api/v1/deals/oftheday/BR/manaus"
CLK = "http://www.clikey.com.br/"   #Clikey Manaus
BTM = "http://www.botomaluco.com.br"
sites={}
sites['Tambaqui Urbano'] = TBQURBANO
sites['Groupon'] = GPN
sites['Clikey'] = CLK
SITES_INCOMPLETE_URL = ["Tambaqui Urbano"]

USER_AGENTS = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1','Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2','Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0','Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00','Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25']

#------------------------------------------------------------
def select_user_agent():
   index = random.randrange(len(USER_AGENTS))
   return USER_AGENTS[index]

#------------------- RE Tambaqui Urbano -------------------------

RETBQdesc = r'<div class="destaque">\n[ ]+<h1><b>(.*)</b>(.*)</h1>'
RETBQlinkimg = r'\n.*<div id="img-produto">\n[ ]*<a href="([^"]+)"><img .*src="([^"]+)" />'
RETBQmain = RETBQdesc + RETBQlinkimg

RETBQLink =  r'<a href="([^"]*)">'
RETBQImg = r'<img.*src="([^"]*)".*</a>'
RETBQDesc = r'\n.*<a.*<b>(.*)</b>(.*)</a>'
RETBQ = RETBQLink + RETBQImg + RETBQDesc

#------------------ Crawler Tambaqui Urbano --------------------------

def tbqCrawler():
	try:
		req = urllib2.Request(TBQURBANO)
		req.add_header = ('User-agent',select_user_agent())
		page = urllib2.urlopen(req)
	except httplib.HTTPException:		
		logging.error("TAMBAQUI FAILED")
		return None,None,None
	
#	enc = page.headers['content-type'].split('charset=')[-1]
	enc = 'ISO-8859-1'
#	enc = 'UTF'
	page_unicoded = unicode(page.read(), enc)
	#final_page = page_unicoded.encode('utf-8')

	o1 = re.search(RETBQmain, page_unicoded) #search the main offer
	link1 = re.sub("/comprar/","/oferta/",o1.group(3))
	offer1 = [[TBQURBANO+link1,TBQURBANO+'/'+o1.group(4),o1.group(1),o1.group(2)]]
	offers = re.findall(RETBQ, page_unicoded)

	offers_temp = []
	for i in offers:
		offers_temp.append([TBQURBANO+i[0],TBQURBANO+'/'+i[1],i[2],i[3]])

	offer1.extend(offers_temp)
	
	offers,linkoffers_to_del,db_offers = deduplication(offer1,"Tambaqui Urbano")	
	logging.info("TAMBAQUI OK")
	return offers,linkoffers_to_del,db_offers

#----------------- RE Groupon ---------------------------------
# http://api.groupon.de/feed/api/v1/deals/oftheday/BR/manaus
REGPNimg = r'<img style="float:left" src="([^"]*)"/>'
REGPNdesc = r'<br />([^<]*)'

#----------------- Crawler Groupon ---------------------------
def gpnCrawler():
	try:
		req = urllib2.Request(GPN)
		req.add_header = ('User-agent',select_user_agent())

		page = urllib2.urlopen(req)
	except httplib.HTTPException:
		logging.error("GROUPON FAILED")
		return None,None,None
	
	xml_page = minidom.parseString(page.read())

	items = xml_page.getElementsByTagName("item")
	
	offers = []
	for item in items:
		offer = []
		img_desc_txt = item.childNodes[5].childNodes[0].nodeValue		
		img_and_desc = re.search(REGPNimg+REGPNdesc,img_desc_txt)
		offer.append(item.childNodes[3].childNodes[0].nodeValue)  #offer link
		offer.append(img_and_desc.group(1))			#img link
		offer.append(img_and_desc.group(2))  #description
		offer.append('')                     #price (null for a while)

		offers.append(offer)
	offers,linkoffers_to_del,db_offers = deduplication(offers,"Groupon")	
	logging.info("GROUPON OK")
	return offers,linkoffers_to_del,db_offers

#----------------- RE Clikey ---------------------------------
RECLKdesc = r'<h1><span class="txt-laranja">Clikey Oferta:</span>(.*)</h1>' 
RECLKimg = r'<div id="s4">\n.*<img .* src="([^"]*)".*</div>' 
RECLKlink = r'<div id="s4">\n.*<a href="([^"]*)">' 

RECLKLinks = r'<center>[\s]*<a href="([^"]*)".*/>[\s]' 

#----------------- Crawler Clikey ---------------------------

def clkCrawler():

	offers = []
	links = []

	try:
		page = urllib2.urlopen(CLK)
	except httplib.HTTPException:
		return None,None,None

	enc = 'ISO-8859-1'
	page_unicoded = unicode(page.read(), enc)		

	desc = re.search(RECLKdesc,page_unicoded).group(1)
	img = CLK+re.search(RECLKimg,page_unicoded).group(1)
	link = re.search(RECLKlink,page_unicoded).group(1)
	link = re.sub("/comprar/","/oferta/",link)

	offers.append([link,img,desc,''])

	links.extend(re.findall(RECLKLinks,page_unicoded))
	
	num_offers = len(links)

	for i in range(num_offers):
		try:
			page = urllib2.urlopen(links[i])
		except httplib.HTTPException:
			logging.error("CLIKEY FAILED")
			return None
		
		enc = 'ISO-8859-1'
		page_unicoded = unicode(page.read(), enc)		

		desc = re.search(RECLKdesc,page_unicoded).group(1)
		img = CLK+re.search(RECLKimg,page_unicoded).group(1)
		link = re.search(RECLKlink,page_unicoded).group(1)
		link = re.sub("/comprar/","/oferta/",link)

		offers.append([link,img,desc,''])
	offers,linkoffers_to_del,db_offers = deduplication(offers,"Clikey")	
	logging.info("CLIKEY OK")
	return offers,linkoffers_to_del,db_offers


#------------------ RE Boto Maluco ------------------------
#------------!!! Aqui se faz uso do  Beautiful Soup -------

#------------------ Crawler Boto Maluco --------------------
def btmCrawler():
	offers = []

	try:
		page = urllib2.urlopen(BTM)
	except httplib.HTTPException:
		return None,None,None

	enc = 'ISO-8859-1'
#	page_unicoded = unicode(page.read(), enc)		

	soup = BeautifulSoup(''.join(page.read()))

	main_offer = soup.find(id="deal-intro")
	link = BTM+main_offer('h1')[0]('a')[0]['href']
	desc = main_offer('h1')[0]('a')[0].next.next[2:]
	img = main_offer('img')[0]['src']
	offers.append([link,img,desc,''])

	table_offers = soup('table')[3]
	num_tr = len(table_offers('tr'))
	for i in xrange(0,num_tr,2):
		html_offer = table_offers('tr')[i]
		link = BTM+html_offer('a')[0]['href']
		img = html_offer('img')[0]['src']
		desc = html_offer('a')[2].string

		offers.append([link,img,desc,''])
	offers,linkoffers_to_del,db_offers = deduplication(offers,"Boto Maluco")
	logging.info("Boto Maluco OK")
	return offers,linkoffers_to_del,db_offers



#-----------------------------------------------------------
def deduplication(offers,site):

	db_offers = db.GqlQuery('SELECT * FROM Offer WHERE site_name=:1',site).fetch(40)
	db_offers = list(db_offers)
	db_mapoffers = {}	
	for o in db_offers:
		db_mapoffers[o.link] = 1		
	
	#Ofertas que estao no dicionario mas nao aparecem nas ofertas do site serao removidas
	#Ofertas que estao no dicionario e estao nas ofertas do site continuarao intactas
	#Ofertas que nao estao no dicionario serao adicionadas para a base de dados
	offers_to_add = []
	linkoffers_to_del = [i.link for i in db_offers]

	for o in offers:
		if db_mapoffers.get(o[0],0) == 0:
			offers_to_add.append(o)
		else:
			db_mapoffers[o[0]] = 0

	for o in db_mapoffers:
		if db_mapoffers[o] == 0:
			linkoffers_to_del.remove(o)

	return offers_to_add,linkoffers_to_del,db_offers



	#-----------Lista para excluir, ofertas desatualizadas do banco----------------
#	offers_to_del = []
#	for i in db_offers:
#		if i.link in linkoffers_to_del:
#			offers_to_del.append(i)
#			linkoffers_to_del.remove(i.link)
#
#	logging.info("A Deletar: "+str(len(offers_to_del)))
#	logging.info("No Banco: "+str(len(db_offers)))
#	return offers_to_add,offers_to_del

