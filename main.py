import webapp2
app = webapp2.WSGIApplication([(r'/','core.views.Index'),
								(r'/faleconosco','core.views.Faleconosco'),
							   (r'/cron/addoffers','core.addOffersToDB.Main'),
								(r'/cron/necessary','core.necessary.Index'),
								(r'/page/(\d)','core.views.Pagination'),
								 (r'/offers/images/(\d+)','core.views.GetImage'),
								 (r'/offers/offer/(\d+)','core.views.OfferPage'),
								 (r'/cron/tbqcrawler','core.addOffersToDB.TambaquiUrbano'),
								 (r'/cron/clkcrawler','core.addOffersToDB.Clikey'),
								 (r'/cron/gpncrawler','core.addOffersToDB.Groupon'),
								 (r'/cron/btmcrawler','core.addOffersToDB.BotoMaluco')],debug=True)
