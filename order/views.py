from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from order_the_food.order.models import Order, OrderForm
from django.forms import ModelForm
import datetime

def index(request, order_date = None):
	if not order_date:
		order_date = datetime.date.today()
	order_list = Order.objects.all().order_by('-delivery_date')
	date_set = sorted(list(set(o.delivery_date for o in order_list if o.delivery_date>=datetime.date.today()-datetime.timedelta(days=7))))

	order_set = Order.objects.filter(delivery_date=order_date)
	order_total = sum(list(o.price for o in order_set))

	return render_to_response('order/index.html', {'date_set': date_set, 'order_date': order_date, 'order_set': order_set, 'order_total': order_total})

def new(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            d = form.cleaned_data['delivery_date']
            return HttpResponseRedirect('/' + str(d))

    else:
        form = OrderForm()

    return render_to_response('order/new.html', {'form': form})

def cancel(request):
    
    order = get_object_or_404(Order, id=request.POST['id'])
    
    if 'confirm' in request.POST:
        order.delete()
        return HttpResponseRedirect('/'+str(order.delivery_date))
    else:
        if 'id' not in request.POST:
            return HttpResponse('Bad request: missing required POST field "id"')
        return render_to_response('order/conf.html', {'order':order})
        