import unittest
from unittest.mock import MagicMock
from unittest import mock
from servicenow_pyclient import SNClient, SNEmptyContent, SNException


class TestSNAPIClient(unittest.TestCase):
    def setUp(self) -> None:
        # Create a mock session to replace requests.Session()
        self.mock_session = MagicMock(name='session')
        self.mock_response = MagicMock(name='response')
        self.mock_session.return_value = self.mock_response

        # Create a test instance of the SNAPIClient
        self.sn_client = SNClient(
            url="https://example.com",
            username="test_user",
            password="test_password",
            enable_push_changes=False,
        )
        self.sn_client._session = self.mock_session

    def test_init(self) -> None:
        # Check if the constructor initializes the object correctly
        self.assertEqual(self.sn_client._base_url, "https://example.com")
        self.assertEqual(self.sn_client._username, "test_user")
        self.assertEqual(self.sn_client._password, "test_password")
        self.assertFalse(self.sn_client._enable_push_changes)

    @mock.patch('servicenow_pyclient.SNClient._request')
    def test_get_table_records(self, mock_request) -> None:
        # Establish
        table_name = "incident"
        sysparm_query = "active=true"
        sysparm_fields = "number,short_description"
        sysparm_display_value = 'false'
        sysparm_limit = 20

        expected_url = f'https://example.com/api/now/table/{table_name}?sysparm_query={sysparm_query}&sysparm_fields={sysparm_fields}&sysparm_display_value={sysparm_display_value}&sysparm_limit={sysparm_limit}'

        # Execute
        response = self.sn_client.get_table_records(
            table_name=table_name,
            query=sysparm_query,
            fields=sysparm_fields,
            display_value='false',
            limit=sysparm_limit,
        )

        # Expectations
        # Check that the URL is constructed correctly
        mock_request.assert_called_with(request_type='GET', url=expected_url)

    @mock.patch('servicenow_pyclient.SNClient._request')
    def test_get_table_record(self, mock_request) -> None:
        # Establish
        table_name = "incident"
        sys_id = '123456'

        expected_url = f'https://example.com/api/now/table/{table_name}/{sys_id}?sysparm_display_value=false'

        # Execute
        response = self.sn_client.get_table_record(
            table_name=table_name,
            sys_id=sys_id
        )

        # Expectations
        # Check that the URL is constructed correctly
        mock_request.assert_called_with(request_type='GET', url=expected_url)

    @mock.patch('servicenow_pyclient.SNClient._request')
    def test_put_table_record(self, mock_request) -> None:
        # Establish
        table_name = "incident"
        sys_id = "123456"
        data = {'key1': 'value1'}

        expected_url = f'https://example.com/api/now/table/{table_name}/{sys_id}?sysparm_display_value=false'

        # Execute
        response = self.sn_client.put_table_record(
            table_name=table_name,
            sys_id=sys_id,
            data=data
        )

        # Expectations
        mock_request.assert_called_with(request_type='PUT', url=expected_url, data=data)

    @mock.patch('servicenow_pyclient.SNClient._request')
    def test_post_table_record(self, mock_request):
        # Establish
        table_name = "incident"
        data = {'key1': 'value1'}

        expected_url = f'https://example.com/api/now/table/{table_name}?sysparm_display_value=false'

        # Execute
        response = self.sn_client.post_table_record(
            table_name=table_name,
            data=data
        )

        # Expectations
        mock_request.assert_called_with(request_type='POST', url=expected_url, data=data)

    @mock.patch('servicenow_pyclient.SNClient._request')
    def test_call_api_now(self, mock_request):
        # Establish
        data = {'key1': 'value1'}

        expected_url = f'https://example.com/api/now/my_url'

        # Execute
        response = self.sn_client.call_api_now(
            request_type='POST',
            url='my_url',
            data=data
        )

        # Expectations
        mock_request.assert_called_with(request_type='POST', url=expected_url, data=data)

        # Subtest #2 - No data is given
        # Establish
        expected_url = f'https://example.com/api/now/my_url2'

        # Execute
        response = self.sn_client.call_api_now(request_type='GET', url='my_url2')

        # Expectations
        mock_request.assert_called_with(request_type='GET', url=expected_url, data={})

    def test_request_enable_push_changes_True(self):
        # Establish - GET
        url = 'my_url'
        data = {'key1': 'value1'}
        self.sn_client._enable_push_changes = True

        expected_json_response = {'key1': 'value1'}
        self.sn_client._session.get().json.return_value = {'result': expected_json_response}

        # Execute, Test GET
        response = self.sn_client._request(request_type='GET', url=url, data=data)
        self.assertEqual(expected_json_response, response)

        # Expectations
        self.sn_client._session.get.assert_called_with(url=url, auth=('test_user', 'test_password'),
                                                       headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                                                       data='{"key1": "value1"}')

        # Establish - POST
        self.sn_client._session.post().json.return_value = {'result': expected_json_response}
        # Execute, Test POST
        response = self.sn_client._request(request_type='POST', url=url, data=data)

        # Expectations
        self.sn_client._session.post.assert_called_with(url=url, auth=('test_user', 'test_password'),
                                                        headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                                                        data='{"key1": "value1"}')
        self.assertEqual(expected_json_response, response)

        # Establish - PUT
        self.sn_client._session.put().json.return_value = {'result': expected_json_response}

        # Execute, Test PUT
        response = self.sn_client._request(request_type='PUT', url=url, data=data)

        # Expectations
        self.sn_client._session.put.assert_called_with(url=url, auth=('test_user', 'test_password'),
                                                       headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                                                       data='{"key1": "value1"}')
        self.assertEqual(expected_json_response, response)

        # Establish - DELETE
        self.sn_client._session.delete().json.return_value = {'result': expected_json_response}

        # Execute, Test DELETE
        response = self.sn_client._request(request_type='DELETE', url=url, data=data)

        # Expectations
        self.sn_client._session.delete.assert_called_with(url=url, auth=('test_user', 'test_password'),
                                                          headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                                                          data='{"key1": "value1"}')
        self.assertEqual(expected_json_response, response)

    @mock.patch('servicenow_pyclient.logger')
    def test_request_enable_push_changes_False(self, mock_logger):
        # Establish
        url = 'my_url'
        data = {'key1': 'value1'}
        self.sn_client._enable_push_changes = False

        # Execute - Test GET
        response = self.sn_client._request(request_type='GET', url=url, data=data)

        # Expectations - Only GET calls can be called when _push_changes is set to False
        self.sn_client._session.get.assert_called_with(url=url, auth=('test_user', 'test_password'),
                                                       headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                                                       data='{"key1": "value1"}')

        # Execute, Test POST
        response = self.sn_client._request(request_type='POST', url=url, data=data)

        # Expectations
        self.sn_client._session.post.assert_not_called()
        self.assertEqual({}, response)
        mock_logger.warning.assert_called_with('SNClient.enable_push_changes is set to False. [POST, PUT, DELETE] requests will not be executed.')

        # Execute, Test PUT
        response = self.sn_client._request(request_type='PUT', url=url, data=data)

        # Expectations
        self.sn_client._session.put.assert_not_called()
        self.assertEqual({}, response)
        mock_logger.warning.assert_called_with('SNClient.enable_push_changes is set to False. [POST, PUT, DELETE] requests will not be executed.')

        # Execute, Test DELETE
        response = self.sn_client._request(request_type='DELETE', url=url, data=data)

        # Expectations
        self.sn_client._session.delete.assert_not_called()
        self.assertEqual({}, response)
        mock_logger.warning.assert_called_with('SNClient.enable_push_changes is set to False. [POST, PUT, DELETE] requests will not be executed.')

    def test_request_202_response(self):
        # Establish
        url = 'my_url'
        data = {'key1': 'value1'}
        self.sn_client._push_changes = True

        mock_response = MagicMock(name='response')
        mock_response.status_code = 202
        self.sn_client._session.get.return_value = mock_response

        # Execute & Expect SNAPIEmptyContent exception
        with self.assertRaises(SNEmptyContent):
            response = self.sn_client._request(request_type='GET', url=url, data=data)

    def test_request_RequestException(self):
        # Establish
        from requests import RequestException
        url = 'my_url'
        data = {'key1': 'value1'}
        self.sn_client._enable_push_changes = True

        self.sn_client._session.get().json.return_value = {'result': {'error': 'My Error'}}
        self.sn_client._session.get().raise_for_status.side_effect = RequestException

        # Execute & Expect RequestException
        with self.assertRaises(SNException):
            response = self.sn_client._request(request_type='GET', url=url, data=data)

        self.sn_client._session.get().json.return_value = {'error': 'My Error'}
        self.sn_client._session.get().raise_for_status.side_effect = RequestException

        # Execute & Expect RequestException
        with self.assertRaises(SNException):
            response = self.sn_client._request(request_type='GET', url=url, data=data)

    def test_request_No_data_given(self):
        # Establish - GET
        url = 'my_url'

        # Execute, Do not pass in data
        response = self.sn_client._request(request_type='GET', url=url)

        # Expectations
        self.sn_client._session.get.assert_called_with(url=url, auth=('test_user', 'test_password'),
                                                       headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                                                       data='{}')

    def tearDown(self):
        # Clean up resources if needed
        pass


class TestSNEmptyContentException(unittest.TestCase):
    def test_exception_attributes(self):
        req_err = {}
        sn_err = {
            'error': {
                'message': 'Custom Message',
                'type': 'Custom Type',
                'detail': 'Custom Detail'
            }
        }

        exception = SNEmptyContent(req_err, sn_err)

        self.assertEqual(exception.error_msg, 'Custom Message')
        self.assertEqual(exception.error_type, 'Custom Type')
        self.assertEqual(exception.error_detail, 'Custom Detail')

    def test_default_attributes(self):
        req_err = {}
        sn_err = {}

        exception = SNEmptyContent(req_err, sn_err)

        self.assertEqual(exception.error_msg, '<empty>')
        self.assertEqual(exception.error_type, '<empty>')
        self.assertEqual(exception.error_type, '<empty>')

    def test_exception_string_representation(self):
        req_err = {}
        sn_err = {
            'error': {
                'message': 'Custom Message',
                'type': 'Custom Type',
                'detail': 'Custom Detail'
            }
        }

        exception = SNEmptyContent(req_err, sn_err)
        exception_str = str(exception)

        expected_str = 'Message: "Custom Message" Type: "Custom Type" Details: "Custom Detail"'
        self.assertEqual(exception_str, expected_str)


class TestSNAPIException(unittest.TestCase):
    def test_exception_attributes(self):
        req_err = {}
        sn_err = {
            'error': {
                'message': 'Custom Message',
                'type': 'Custom Type',
                'detail': 'Custom Detail'
            }
        }

        exception = SNException(req_err, sn_err)

        self.assertEqual(exception.error_msg, 'Custom Message')
        self.assertEqual(exception.error_type, 'Custom Type')
        self.assertEqual(exception.error_detail, 'Custom Detail')

    def test_default_attributes(self):
        req_err = {}
        sn_err = {}

        exception = SNException(req_err, sn_err)

        self.assertEqual(exception.error_msg, '<empty>')
        self.assertEqual(exception.error_type, '<empty>')
        self.assertEqual(exception.error_detail, '<empty>')

    def test_exception_string_representation(self):
        req_err = {}
        sn_err = {
            'error': {
                'message': 'Custom Message',
                'type': 'Custom Type',
                'detail': 'Custom Detail'
            }
        }

        exception = SNException(req_err, sn_err)
        exception_str = str(exception)

        expected_str = 'Message: "Custom Message" Type: "Custom Type" Details: "Custom Detail"'
        self.assertEqual(expected_str, exception_str)


if __name__ == '__main__':
    unittest.main()
