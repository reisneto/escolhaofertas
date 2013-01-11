from google.appengine.ext import db

class Offer(db.Model):
	link = db.StringProperty()
	img = db.StringProperty()  #image link
	image = db.BlobProperty(default=None)  #image itself
	desc = db.StringProperty()
	price = db.StringProperty()

	site_name = db.StringProperty()   #nome site do qual foi coletada a oferta
	views = db.IntegerProperty()

