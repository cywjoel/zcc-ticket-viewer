from app import *
from unittest import TestCase, main, mock

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
    
# class TestRequestMethods(Testcase):
#     @mock.patch(app.requests.get)
#     def test_init_paginate(self, mock_ticket_page):
#         mock_response = mock.Mock(status_code=200)
#         mock_response.json.return_value =

if __name__ =='__main__':
    main()
