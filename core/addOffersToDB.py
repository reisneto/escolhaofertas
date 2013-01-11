from datetime import datetime
import logging
import resites
import webapp2
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from models import Offer
#--------------- GLOBAL VARIABLES -----------------------

TBQURBANO = "http://www.tambaquiurbano.com/" 
GPN ="http://api.groupon.de/feed/api/v1/deals/oftheday/BR/manaus"
CLK = "http://www.clikey.com.br/?cdd=1"   #Clikey Manaus
BTM = "http://www.botomaluco.com.br"
sites={}
sites['Tambaqui Urbano'] = TBQURBANO
sites['Groupon'] = GPN
sites['Clikey'] = CLK
sites['Boto Maluco'] = BTM
SITES_INCOMPLETE_URL = ["Tambaqui Urbano"]
#--------------------------------------------

def addOffers(self,offers,site):
	if not offers:
		return

	newOffers = []
	for offer in offers:
		try:
			image_offer = urlfetch.Fetch(url=offer[1],deadline=10).content	
		except urlfetch.Error:
			image_offer = urlfetch.fetch(url='http://www.escolhaofertas.com.br/static/images/img_404.png').content
			logging.error("Image Timeout")
		newOffers.append( Offer(link=offer[0],\
					img=offer[1],\
					image = db.Blob(image_offer),\
					 desc=offer[2]+offer[3],\
					 price='',\
					 site_name=site,\
					 views=0
					 ))
	db.put(newOffers)
	memcache.flush_all()
	memcache.set("num_offers",Offer.all().count())
	logging.info("Offers length :" + str(len(newOffers)))
	self.response.out.write(site+": Offers added")
	

def deleteOffers(db_offers,linkoffers_to_del,site):
	if not linkoffers_to_del:
		return

	offers_to_del = []
	for i in db_offers:
		if i.link in linkoffers_to_del:
			offers_to_del.append(i)
			linkoffers_to_del.remove(i.link)

	logging.info("A Deletar: "+str(len(offers_to_del)))
	logging.info("No Banco: "+str(len(db_offers)))


	if offers_to_del:
		db.delete(offers_to_del)
	
class TambaquiUrbano(webapp2.RequestHandler):
	def get(self):
		offers,linkoffers_to_del,db_offers = resites.tbqCrawler()

		deleteOffers(db_offers,linkoffers_to_del,'Tambaqui Urbano')	
		addOffers(self,offers,'Tambaqui Urbano')
		
		self.response.out.write("algorithm finished")
#		TBQ ="http://www.tambaquiurbano.com" 
#		newOffers = []
#		for offer in offers:
#			try:
#				image_offer = urlfetch.Fetch(url=TBQ+'/'+offer[1],deadline=10).content	
#			except urlfetch.Error:
#				image_offer = urlfetch.fetch(url='/static/images/img_404.png').content
#				logging.error("Image Timeout")
#			newOffers.append( Offer(link=TBQ+offer[0],\
#						img=TBQ+'/'+offer[1],\
#						image = db.Blob(image_offer),\
#						 desc=offer[2]+offer[3],\
#						 price='',\
#						 site_name='Tambaqui Urbano',\
#						 views=0
#						 ))
#		db.put(newOffers)
#		memcache.flush_all()
#		memcache.set("num_offers",Offer.all().count())
#		self.response.out.write("Tambaqui Urbano: Offers added")
		

class Groupon(webapp2.RequestHandler):
	def get(self):
		offers,linkoffers_to_del,db_offers = resites.gpnCrawler()

		deleteOffers(db_offers,linkoffers_to_del,'Groupon')
		addOffers(self,offers,'Groupon')
		self.response.out.write("algorithm finished")

class Clikey(webapp2.RequestHandler):
	def get(self):
		offers,linkoffers_to_del,db_offers = resites.clkCrawler()

		deleteOffers(db_offers,linkoffers_to_del,'Clikey')	
		addOffers(self,offers,'Clikey')
		self.response.out.write("algorithm finished")	

class BotoMaluco(webapp2.RequestHandler):
	def get(self):
		offers,linkoffers_to_del,db_offers = resites.btmCrawler()

		deleteOffers(db_offers,linkoffers_to_del,'Boto Maluco')	
		addOffers(self,offers,'Boto Maluco')
		self.response.out.write("algorithm finished")	
	

class Main(webapp2.RequestHandler):
	def get(self):
		pass
		#GPNOffers = resites.gpnCrawler()
		
		#memcache.flush_all()
		#query = Offer.all()
		#offers = query.fetch(100) # number of offers fetched
		#db.delete(offers)
		
		#addGPNOffers(GPNOffers)

		#numOffers = Offer.all().count()
		#memcache.set('num_offers', numOffers)
		#today = datetime.today().strftime("%d/%m/%y")
		#memcache.set('uploaded_date_offers', today)
		#self.response.out.write("New Items added")
 
