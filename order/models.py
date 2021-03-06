# encoding: utf-8

from django.db import models
from django import forms
from django.forms import ModelForm
from django.forms import widgets, fields
from django.contrib.auth.models import User
import datetime
from BeautifulSoup import BeautifulSoup
import urllib2
import re


def generate_menu():
    page = urllib2.urlopen("http://www.kana.ro/meniu.php")
    soup = BeautifulSoup(page)

    V = soup.html.body.findAll('tr')

    days = list(v.string for v in V[0].findAll('td'))
    for d in days:
        d = d.capitalize()

    V1         = list(v.string for v in V[2].findAll('td'))
    V2         = list(v.string for v in V[12].findAll('td'))
    V3         = list(v.string for v in V[22].findAll('td'))
    V4         = list(v.string for v in V[32].findAll('td'))
    Vegetarian = list(v.string for v in V[42].findAll('td'))
    S1         = list(v.string for v in V[52].findAll('td'))
    S2         = list(v.string for v in V[62].findAll('td'))

    menu = {'days':days, 'V1':V1, 'V2':V2, 'V3':V3, 'V4':V4, 'Vegetarian':Vegetarian, 'S1':S1, 'S2':S2}

    return menu

class ClosedOrder(models.Model):
    delivery_date = models.DateField(verbose_name=u"Data livrarii")

    def __unicode__(self):
        return unicode(self.delivery_date)

class Order(models.Model):
    user = models.ForeignKey(User, verbose_name="Utilizator")
    delivery_date = models.DateField(verbose_name=u"Data livrării")
    order = models.CharField(max_length=100, verbose_name="Comanda")
    price = models.FloatField(verbose_name=u"Prețul comenzii (în RON)")
    
    def __unicode__(self):
        return self.order

class OrderContent(object):
    def __init__(self, item1='', item2='', item3=''):
        self.item1 = item1
        self.item2 = item2
        self.item3 = item3

class OrderContentWidget(widgets.MultiWidget):
    def __init__(self, attrs=None):
        menu = {}
        menu = generate_menu()

        widgets = (forms.Select(choices=(
                                            ('V1','V1'),
                                            ('V2','V2'),
                                            ('V3','V3'),
                                            ('V4','V4'),
                                            ('Vegetarian','Vegetarian'),
                                            ('S1','S1'),
                                            ('S2','S2')
                                        )),
                   forms.Select(choices=(
                                            ('-','-'),
                                            ('V1','V1'),
                                            ('V2','V2'),
                                            ('V3','V3'),
                                            ('V4','V4'),
                                            ('Vegetarian','Vegetarian'),
                                            ('S1','S1'),
                                            ('S2','S2')
                                        )),
                   forms.Select(choices=(
                                            ('-','-'),
                                            ('V1','V1'),
                                            ('V2','V2'),
                                            ('V3','V3'),
                                            ('V4','V4'),
                                            ('Vegetarian','Vegetarian'),
                                            ('S1','S1'),
                                            ('S2','S2')
                                        )))

        super(OrderContentWidget, self).__init__(widgets, attrs=attrs)

    def decompress(self, value):
        if value:
            return [value.item1, value.item2, value.item3]
        return [None, None, None]

class OrderContentField(fields.MultiValueField):
    widget = OrderContentWidget
    def __init__(self, required=False, widget=None, label=None, initial=None):
        fields = (forms.fields.CharField(), forms.fields.CharField(), forms.fields.CharField())
        super(OrderContentField, self).__init__(fields=fields, widget=widget, label=label, initial=initial)

    def compress(self, data_list):
        if data_list:
            return OrderContent(data_list[0], data_list[1], data_list[2])
        return None

def date_choices():
    weekdays = ('Luni', 'Marți', 'Miercuri', 'Joi', 'Vineri')
    l = []
    
    for i in range(0,8):
        d = datetime.date.today() + datetime.timedelta(i)

        orders = list(Order.objects.filter(delivery_date=d))

        closed_orders = list(ClosedOrder.objects.all())
        
        if (d.weekday() < len(weekdays)) and (d not in closed_orders):        
            l.append( ( d, ("%s (%s)" % (str(d), weekdays[d.weekday()]) ) ) )
    return l

class OrderForm(ModelForm):
    delivery_date = forms.DateField(widget=forms.Select(choices=()), label='Data livrării')
    order = OrderContentField()

    def __init__(self, *args, **kwargs):
    	super(OrderForm, self).__init__(*args, **kwargs)

	self.fields['delivery_date'].widget.choices = date_choices()

    def save(self):
        prices = {'V1':10.5, 'V2':10.5, 'V3':10.5, 'V4':4.0, 'Vegetarian':10.5, 'S1':10.5, 'S2':10.5, '-':0.0}
        self.instance.price = prices[self.data['order_0']]+prices[self.data['order_1']]+prices[self.data['order_2']]
        super(OrderForm, self).save()

    class Meta:
        model = Order
        exclude = ('price', 'sent')

    def clean_user(self):
        thisone = self.cleaned_data['user']
        
        l = Order.objects.filter(delivery_date = self.data['delivery_date'])
        if thisone in set(u.user for u in l):
            raise forms.ValidationError(u'Un user nu poate avea mai mult de o comandă pe zi.')

        return thisone

    def clean_order(self):
        thisorder = self.cleaned_data['order']
        if (thisorder.item2 != '-' and thisorder.item3 != '-'):
            o = thisorder.item1+'+'+thisorder.item2+'+'+thisorder.item3
        elif (thisorder.item2 != '-' and thisorder.item3 == '-'):
            o = thisorder.item1+'+'+thisorder.item2
        elif (thisorder.item2 == '-' and thisorder.item3 != '-'):
            o = thisorder.item1+'+'+thisorder.item3
        else:
            o = thisorder.item1
        thisorder = o

        return thisorder

