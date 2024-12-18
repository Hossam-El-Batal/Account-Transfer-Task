from django.test import TestCase
from django.urls import reverse
from transactions.models import Account
import json
import uuid

class TransferFundsTestCase(TestCase):
    def setUp(self):
        self.sender_id = uuid.uuid4()
        self.receiver_id = uuid.uuid4()
        
        self.sender = Account.objects.create(
            id=self.sender_id, 
            name="Sender", 
            balance=1000
        )
        self.receiver = Account.objects.create(
            id=self.receiver_id, 
            name="Receiver", 
            balance=500
        )
        
        self.url = reverse('transfer_funds')

    def test_successful_transfer(self):
        transfer_data = {
            'sender_id': str(self.sender_id), 
            'receiver_id': str(self.receiver_id), 
            'amount': 100
        }
        response = self.client.post(
            self.url, 
            data=json.dumps(transfer_data), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        self.sender.refresh_from_db()
        self.receiver.refresh_from_db()
        
        self.assertEqual(self.sender.balance, 900)
        self.assertEqual(self.receiver.balance, 600)

    def test_missing_fields(self):
        response = self.client.post(
            self.url, 
            data=json.dumps({'sender_id': str(self.sender_id)}), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_non_existent_sender(self):
        non_existent_id = uuid.uuid4()
        transfer_data = {
            'sender_id': str(non_existent_id), 
            'receiver_id': str(self.receiver_id), 
            'amount': 100
        }
        response = self.client.post(
            self.url, 
            data=json.dumps(transfer_data), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())

    def test_insufficient_funds(self):
        transfer_data = {
            'sender_id': str(self.sender_id), 
            'receiver_id': str(self.receiver_id), 
            'amount': 2000
        }
        response = self.client.post(
            self.url, 
            data=json.dumps(transfer_data), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
####
class ShowBalanceTestCase(TestCase):
    def setUp(self):
        self.account_id = uuid.uuid4()
        self.account = Account.objects.create(
            id=self.account_id, 
            name="Test Account", 
            balance=1000
        )
        self.url = reverse('show_balance', kwargs={'id': self.account_id})

    def test_show_balance(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['Name'], "Test Account")
        self.assertEqual(data['balance'], 1000)

    def test_non_existent_account(self):
        non_existent_id = uuid.uuid4()
        url = reverse('show_balance', kwargs={'id': non_existent_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())

