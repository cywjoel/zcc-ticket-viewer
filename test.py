from app import *
import json
import requests
from urllib.parse import urlparse
from unittest import TestCase, main, mock

# Testing methods for config.json and setting up headers
class TestConfigMethods(TestCase):

    def test_get_user_and_token(self):
        self.assertEqual(get_user_and_token('test_json/test_config.json'), ('joepublic@example.com', '1234567890abcdef'))

    def test_get_subdomain(self):
        self.assertEqual(get_subdomain('test_json/test_config.json'), 'sampledomain')
        self.assertNotEqual(get_subdomain('test_json/test_config.json'), 'notsampledomain')
    
    def test_base64_encode(self):
        user, token = get_user_and_token('test_json/test_config.json')
        self.assertEqual(get_base64_string(user, token), 'am9lcHVibGljQGV4YW1wbGUuY29tL3Rva2VuOjEyMzQ1Njc4OTBhYmNkZWY=')
    
    def test_make_headers(self):
        self.assertEqual(make_headers('test_json/test_config.json'), { 'Authorization': 'Basic am9lcHVibGljQGV4YW1wbGUuY29tL3Rva2VuOjEyMzQ1Njc4OTBhYmNkZWY='})
    
# Testing API requests
class TestApiRequests(TestCase):

    @mock.patch('app.requests.get')
    def test_auth_fail(self, mock_ticket):
        mock_response = mock.Mock(status_code=401)
        with open('test_json/test_401.json') as file:
            mock_response.json.return_value = json.load(file)
            mock_ticket.return_value = mock_response

            r = requests.get('https://example.zendesk.com/api/v2/tickets/25', headers={ 'Authorization': 'Basic bm9lcHVibGljQGV4YW1wbGUuY29tL3Rva2VuOjEyMzQ1Njc4OTBhYmNkZWY='})
            self.assertEqual(r.status_code, 401)
            
            data = r.json()
            self.assertEqual(data['error'], 'Couldn\'t authenticate you')

    @mock.patch('app.requests.get')
    def test_get_ticket_200(self, mock_ticket):
        mock_response = mock.Mock(status_code=200)
        with open('test_json/test_ticket_200.json') as file:
            mock_response.json.return_value = json.load(file)
            mock_ticket.return_value = mock_response

            r = requests.get('https://example.zendesk.com/api/v2/tickets/25', headers={ 'Authorization': 'Basic am9lcHVibGljQGV4YW1wbGUuY29tL3Rva2VuOjEyMzQ1Njc4OTBhYmNkZWY='})
            self.assertEqual(r.status_code, 200)
            
            data = r.json()
            self.assertEqual(data['ticket']['id'], 25)
    
    @mock.patch('app.requests.get')
    def test_get_ticket_404(self, mock_ticket):
        mock_response = mock.Mock(status_code=404)
        with open('test_json/test_ticket_404.json') as file:
            mock_response.json.return_value = json.load(file)
            mock_ticket.return_value = mock_response

            r = requests.get('https://example.zendesk.com/api/v2/tickets/25', headers={ 'Authorization': 'Basic am9lcHVibGljQGV4YW1wbGUuY29tL3Rva2VuOjEyMzQ1Njc4OTBhYmNkZWY='})
            self.assertEqual(r.status_code, 404)
            
            data = r.json()
            self.assertEqual(data['description'], 'Not found')
            self.assertEqual(data['error'], 'RecordNotFound')

    @mock.patch('app.requests.get')
    def test_get_page(self, mock_page):
        mock_response = mock.Mock(status_code=200)
        with open('test_json/test_paginate.json') as file:
            mock_response.json.return_value = json.load(file)
            mock_page.return_value = mock_response

            r = requests.get('https://example.zendesk.com/api/v2/tickets.json?page[size]=25', headers={ 'Authorization': 'Basic am9lcHVibGljQGV4YW1wbGUuY29tL3Rva2VuOjEyMzQ1Njc4OTBhYmNkZWY='})
            self.assertEqual(r.status_code, 200)
            
            data = r.json()
            self.assertEqual(data['links']['next'], 'https://example.zendesk.com/api/v2/tickets.json?page%5Bafter%5D=eyJvIjoibmljZV9pZCIsInYiOiJhUmtBQUFBQUFBQUEifQ%3D%3D&page%5Bsize%5D=25')
            self.assertTrue(data['meta']['has_more'])
            self.assertEqual(len(data['tickets']), 25)

# Testing Flask routes
class TestRoutes(TestCase):

    def test_home_page(self):
        r = app.test_client().get('/')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(b'<title>Zendesk Ticket Viewer</title>' in r.data)
    
    def test_index_zero_redirect(self):
        r = app.test_client().get('/0')
        self.assertEqual(r.status_code, 302)
        self.assertEqual(urlparse(r.location).path, '/')
    
    def test_route_not_exist(self):
        r = app.test_client().get('/fakepage')
        self.assertEqual(r.status_code, 404)
        self.assertTrue(b'The page or ticket you are looking for doesn\'t exist.' in r.data)
    
    def test_unauthorized_redirect(self):
        r = app.test_client().get('/unauthorized')
        self.assertEqual(r.status_code, 302)
        self.assertEqual(urlparse(r.location).path, '/')

if __name__ =='__main__':
    main()
