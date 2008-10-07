# encoding: utf-8

import unittest
from order_the_food.order.models import Order
from django.contrib.auth.models import User
from django.test.client import Client
from django.test import TestCase
import datetime

today = str(datetime.date.today())

class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_details(self):
        # Issue a GET request.
        response = self.client.get('/'+today+'/')

        self.failUnlessEqual(response.status_code, 200)
        
        self.failUnlessEqual(response.context['order_date'], today)

class OrderTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username = 'Victor')
        self.user2 = User.objects.create(username = 'Victor2')
        self.user3 = User.objects.create(username = 'Victor3')
        
    	self.order1 = Order.objects.create(user=self.user, order="V1", delivery_date=datetime.date.today(), price="15.5")
        self.order2 = Order.objects.create(user=self.user2, order="V2", delivery_date=datetime.date.today(), price="14")
        self.order3 = Order.objects.create(user=self.user3, order="V3", delivery_date=datetime.date.today(), price="15.5")
    
    def tearDown(self):
        for order in Order.objects.all():
            order.delete()
        
        self.user.delete()

    def testOrder(self):
        c = Client()

        self.user4 = User.objects.create(username = 'Victor4')
        response_1 = c.post('/new', {'user':self.user4.id, 'delivery_date':datetime.date.today(), 'order':'V1', 'price':'15.5'})
        response_2 = c.get('/'+today+'/')

        self.assertContains(response_2, text='60.5')

    def testOccurence(self):
        c = Client()

        self.user4 = User.objects.create(username = 'Victor4')
        response_1 = c.post('/new', {'user':self.user4.id, 'delivery_date':datetime.date.today(), 'order':'V2', 'price':'14'})
        response_2 = c.get('/'+today+'/')

        self.assertContains(response_2, text='Comenzile pentru ziua de '+today+':')
        self.assertContains(response_2, text='Victor', count=4)
        self.assertContains(response_2, text='V1')
        self.assertContains(response_2, text='V2', count=2)
        self.assertContains(response_2, text='V3')
        self.assertContains(response_2, text='59')
        self.assertContains(response_2, text='15.5', count=2)
        self.assertContains(response_2, text='14', count=2)

    def testUser(self):
        c = Client()
        
        response = c.post('/new', {'user':self.user.id, 'delivery_date':datetime.date.today(), 'order':'V1', 'price':'12'})
        
        self.assertContains(response, text=u'mai mult de o comandă'.encode('utf-8'))

    def testDate(self):
        c = Client()

        response = c.post('/new', {'user':self.user.id, 'delivery_date':datetime.date.today()-datetime.timedelta(1), 'order':'V1', 'price':'12'})
        self.assertContains(response, text=u'trecut'.encode('utf-8'))

        response = c.post('/new', {'user':self.user.id, 'delivery_date':datetime.date.today()+datetime.timedelta(20), 'order':'V1', 'price':'12'})
        self.assertContains(response, text=u'două săptămâni'.encode('utf-8'))

    def testPrice(self):
        c = Client()

        response = c.post('/new', {'user':self.user.id, 'delivery_date':datetime.date.today(), 'order':'V1', 'price':'-2'})
        self.assertContains(response, text=u'Vă rugăm să introduceți o valoare pozitivă.'.encode('utf-8'))

        response = c.post('/new', {'user':self.user.id, 'delivery_date':datetime.date.today(), 'order':'V1', 'price':'145'})
        self.assertContains(response, text=u'Suma introdusă este prea mare.'.encode('utf-8'))

