import os
import webapp2
import jinja2
import json
import logging
from models import Offer
from google.appengine.api import memcache
from google.appengine.api import mail
from google.appengine.ext import db
from datetime import datetime

template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),\
				autoescape=True)
divs_offer = """
<div class="offer">
	<a class="link-offer" rel="nofollow" href="%s" target="_blank">
		<h1 class="title-offer"> %s </h1>
	</a>
	<img class="img-offer" src="%s" alt="link offer"/> 
	<div class="details-offer"> 
		<a rel="nofollow" href="%s" target="_blank"> Ver Mais </a>
   	</div>
	<span> Fonte: %s </span>
</div>
"""

PAGESIZE = 10

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
	

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)	

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class Index(Handler):
	def get(self):
		numOffers = memcache.get('num_offers')
		t = datetime.today() 
		uploaded_date_offers = t.strftime("%d/%m/%y")

		offers = Offer.all().order("__key__").fetch(PAGESIZE)
		offers = list(offers)
		#uploaded_date_offers = memcache.get('last_update')
		self.render('index.html', offers=offers, num_offers=numOffers, uploaded_date_offers=uploaded_date_offers)
		

class OfferPage(Handler):
	def get(self, page_id):
		offer = memcache.get("page"+page_id)

		if not offer:
			offer = Offer.get_by_id(int(page_id))
			memcache.set("page"+page_id,offer)

		if offer:
			self.render('index.html',offers=[offer],num_offers=-1, uploaded_date_offers=None)
		else:
		 	self.redirect('/static/pages/404.html')

class Faleconosco(Handler):
	def get(self):
		self.render('faleconosco.html')

	def post(self):
		name = self.request.get("name")
		email = self.request.get("email")
		subject = self.request.get("subject")
		message = self.request.get("message")

		mail_msg = mail.EmailMessage(sender="Suporte Escolha Ofertas <suporte@escolhaofertas.com.br>",
									subject= "[%s] %s" % (subject,name))
		mail_msg.to = "reisneto@escolhaofertas.com.br"
		mail_msg.body = """
		Nome: %s
		Email: %s
		Mensagem:
		%s
		""" % (name,email,message)
		mail_msg.send()
		self.redirect("/")

class Pagination(Handler):		
	def createJsonOffers(self,page,offers,more=1):
		jsonOffers = [{'link':o.link,
					'desc':o.desc,
					'img':o.img,
					'id':o.key().id(),
					'site_name':o.site_name,
					'more':more}for o in offers]
		memcache.add("offers_page"+page,jsonOffers)
		return jsonOffers

	def get(self, page):
		offers_page = memcache.get("offers_page"+page)
		if offers_page is not None:
			logging.info("offers_page"+str(page)+" HIT")
			self.response.out.write(json.dumps(offers_page))
			return

		offers = Offer.all().order("__key__").fetch(PAGESIZE + 1, (int(page)-1) * PAGESIZE)
		num_offers = len(offers)

		offers = offers[:PAGESIZE]
		if num_offers == PAGESIZE+1:
			response = self.createJsonOffers(page,offers)
		elif num_offers > 0:
			response = self.createJsonOffers(page,offers,0)
		else:
			response = '{more:-1}'

		memcache.set("offers_page"+page,response)
		logging.info("offers_page"+str(page)+" Miss")
		self.response.out.write(json.dumps(response))

class GetImage(Handler):
	def	get(self,image_id):
		offer = Offer.get_by_id(int(image_id))
		self.response.headers['Content-Type'] = 'image/jpeg'		
		self.response.out.write(offer.image)



