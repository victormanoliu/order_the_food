from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
	(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MY_BASE + 'order_the_food/media'}),
	(r'^admin/(.*)$', admin.site.root),
	(r'^new$', 'order_the_food.order.views.new'),
    	(r'^(?P<order_date>.+)/$', 'order_the_food.order.views.index'),
    (r'^anulare$','order_the_food.order.views.cancel'),
	(r'^$', 'order_the_food.order.views.index'),
)
