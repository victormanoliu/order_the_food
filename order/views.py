from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from order_the_food.order.models import Order, OrderForm, ClosedOrder
from django.forms import ModelForm
import datetime
import time
from django.core.mail import send_mail


def index(request, order_date = None):
    if not order_date:
        order_date = datetime.date.today()
    order_list = Order.objects.all().order_by('-delivery_date')
    seven_days_ago = datetime.date.today()-datetime.timedelta(days=7)
    date_set = list(set(o.delivery_date for o in order_list if o.delivery_date>=seven_days_ago))
    date_set.reverse()

    temp_list = []

    order_set = Order.objects.filter(delivery_date=order_date)

    closed_dates = list(str(c.delivery_date) for c in ClosedOrder.objects.all())

    if order_date not in closed_dates:
        sent = 0
    else:
        sent = 1

    for o in order_set:
		x = str(o.order).split('+')
		for i in x:
			temp_list.append(i)

    temp_set = set(temp_list)
	
    order_summary = []

    for i in temp_set:
        order_summary.append({ 'what': i, 'count': temp_list.count(i) })
    order_summary.sort()

    order_total = sum(list(o.price for o in order_set))

    return render_to_response('order/index.html', {'date_set': date_set, 'order_date': order_date, 'order_set': order_set, 'order_total': order_total, 'order_summary': order_summary, 'sent': sent})

def new(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            closed_dates = list(str(c.delivery_date) for c in ClosedOrder.objects.all())

            d = str(form.cleaned_data['delivery_date'])

            if d not in closed_dates:
                form.save()
            return HttpResponseRedirect('/' + d)

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

def close(request):
    order_date = str(request.POST['order_date'])
    #c = time.strptime(order_date,"%Y-%m-%d")
    #order_date = datetime.date(c[0],c[1],c[2])

    if 'confirm' in request.POST:
        if request.POST['parola'] == 'david':
            c = ClosedOrder(delivery_date = order_date)
            c.save()

            return HttpResponseRedirect('/'+str(order_date))
        else:
            return render_to_response('order/close.html', {'order_date':order_date, 'prompt':'PAROLĂ INCORECTĂ'})
        
    else:
        return render_to_response('order/close.html', {'order_date':order_date, 'prompt':''})
        
