import json
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from udj.models import Ticket

class ReissueAuthTest(TestCase):
  fixtures = ['test_fixture']
  client = Client()
  lucas = User.objects.get(username='lucas')

  def issueTicketRequest(self):
    return self.client.post(
        '/udj/0_6/auth', {'username': 'lucas', 'password' : 'testlucas'})

  @staticmethod
  def getCurrentTicket():
    return Ticket.objects.get(user=ReissueAuthTest.lucas)

  def testReissue(self):
    self.assertTrue(Ticket.objects.filter(user=ReissueAuthTest.lucas).exists())
    oldTicket = ReissueAuthTest.getCurrentTicket()

    response = self.issueTicketRequest()

    self.assertEqual(response.status_code, 200, response.content)
    self.assertEqual(response['Content-Type'], 'text/json; charset=utf-8')


    newTicket = ReissueAuthTest.getCurrentTicket()

    self.assertNotEqual(oldTicket.ticket_hash, newTicket.ticket_hash)
    self.assertTrue(oldTicket.time_issued < newTicket.time_issued)



class AuthTests(TestCase):
  fixtures = ['test_fixture']
  client = Client()
  kurtis = User.objects.get(username='kurtis')

  def issueTicketRequest(self, username='kurtis', password='testkurtis'):
    return self.client.post(
        '/udj/0_6/auth', {'username': username, 'password' : password})

  @staticmethod
  def getCurrentTicket():
    return Ticket.objects.get(user=AuthTests.kurtis)

  def testAuth(self):
    response = self.issueTicketRequest()

    self.assertEqual(response.status_code, 200, response.content)
    self.assertEqual(response['Content-Type'], 'text/json; charset=utf-8')

    ticket_and_user_id = json.loads(response.content)
    ticket_hash = ticket_and_user_id['ticket_hash']
    user_id = ticket_and_user_id['user_id']

    self.assertEqual(user_id, AuthTests.kurtis.id)
    self.assertEqual(ticket_hash, AuthTests.getCurrentTicket().ticket_hash)

  def testDoubleAuth(self):
    response = self.issueTicketRequest()

    self.assertEqual(response.status_code, 200, response.content)
    self.assertEqual(response['Content-Type'], 'text/json; charset=utf-8')

    ticket_and_user_id = json.loads(response.content)
    ticket_hash = ticket_and_user_id['ticket_hash']
    user_id = ticket_and_user_id['user_id']

    self.assertEqual(user_id, AuthTests.kurtis.id)
    self.assertEqual(ticket_hash, AuthTests.getCurrentTicket().ticket_hash)

    response = self.issueTicketRequest()

    self.assertEqual(response.status_code, 200, response.content)
    self.assertEqual(response['Content-Type'], 'text/json; charset=utf-8')

    ticket_and_user_id = json.loads(response.content)
    new_ticket = ticket_and_user_id['ticket_hash']

    self.assertEqual(new_ticket, ticket_hash)

  def testBadPassword(self):
    response = self.issueTicketRequest(password="badpassword")

    self.assertEqual(response.status_code, 401, response.content)
    self.assertEqual(response['WWW-Authenticate'], 'password')

  def testBadUsername(self):
    response = self.issueTicketRequest(username="wrongwrongwrong")

    self.assertEqual(response.status_code, 401, response.content)
    self.assertEqual(response['WWW-Authenticate'], 'password')
