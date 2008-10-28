from order_the_food.order.models import Order, ClosedOrder
from django.contrib import admin

class OrderAdmin(admin.ModelAdmin):

	fieldsets = [	
			('User',	{'fields':['user']}),
			('Date',	{'fields':['delivery_date']}),
			('Order',	{'fields':['order', 'price']}),
		]

	list_display = ('delivery_date', 'user', 'order', 'price')
	list_filter = ['delivery_date']
	date_hierarchy = 'delivery_date'

class OrderAdmin(admin.ModelAdmin):

	fieldsets = [	
			('Date',	{'fields':['delivery_date']}),
		]

	#list_display = (str('delivery_date'),)
	#date_hierarchy = 'delivery_date'

admin.site.register(Order,OrderAdmin)
admin.site.register(ClosedOrder)

