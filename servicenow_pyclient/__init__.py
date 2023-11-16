import json
import logging

import requests

from servicenow_pyclient.exceptions import SNException, SNEmptyContent

logger = logging.getLogger(__name__)


class SNClient:
    def __init__(self, url: str, username: str, password: str, enable_push_changes=True):
        """
        Initialize a new instance of the SNAPIClient.

        Args:
            url (str): The URL for the ServiceNow Client instance.
            username (str): The username for authentication.
            password (str): The password for authentication.
            enable_push_changes (bool, optional): A flag indicating whether [PUT, POST, DELETE] requests should be pushed.
                GET requests will always be allowed.
                Defaults to True.

        Attributes:
            _base_url (str): The URL for the SNAPIClient service.
            _username (str): The username for authentication.
            _password (str): The password for authentication.
            _push_changes (bool): A flag indicating whether [PUT, POST, DELETE] requests should be pushed. GET requests will always be allowed.
            _session (requests.Session): A session object for making HTTP requests.
        """
        self._base_url = url
        self._username = username
        self._password = password
        self._enable_push_changes = enable_push_changes
        self._session = requests.Session()

    def get_table_api_url(self):
        return f'{self._base_url}/api/now/table/'

    def _request(self, request_type: str, url: str, data=None) -> dict:
        """
        Execute an API request.

        Args:
            request_type (str): The type of HTTP request to execute ('GET', 'POST', 'PUT', 'DELETE').
            url (str): The URL for the API request.
            data (dict, optional): Data to be included in the request, in JSON format.

        Returns:
            dict: The API response as a dictionary.

        Raises:
            SNAPIException: If invalid request type is given.
            SNAPIEmptyContent: If a GET request returns a "202: no content" response.
            SNAPIException: If an error occurs during the API request.

        This method performs an HTTP request to a ServiceNow API endpoint with the specified request type, URL, and optional data.
        It handles different request types ('GET', 'POST', 'PUT', 'DELETE') and includes authentication headers.

        If the request type is 'POST', 'PUT', or 'DELETE', it checks if the `_enable_push_changes` flag is set before making the request.
        If `_enable_push_changes` is False, a warning is logged, and the method returns empty dict without making the request.

        The method checks for HTTP error codes and raises an exception if an error occurs. It also raises `SNAPIEmptyContent`
        if a GET request returns a "202: no content" response.
        """

        if request_type.upper() not in ['GET', 'POST', 'PUT', 'DELETE']:
            sn_error = {'error': {'message': f"'{request_type}' is an invalid request type.", 'type': 'call_api_now',
                                  'detail': f"Request type in call_api_now() must be 'GET', 'POST', 'PUT', 'DELETE'."}}
            raise SNException(req_error=None, sn_error=sn_error)

        auth = (self._username, self._password)

        headers = {"Content-Type": "application/json",
                   "Accept": "application/json"}

        if data is None:
            data = {}

        response = None

        if request_type.upper() == 'GET':
            response = self._session.get(url=url, auth=auth, headers=headers, data=json.dumps(data))
        elif self._enable_push_changes:
            if request_type.upper() == 'POST':
                response = self._session.post(url=url, auth=auth, headers=headers, data=json.dumps(data))
            elif request_type.upper() == 'PUT':
                response = self._session.put(url=url, auth=auth, headers=headers, data=json.dumps(data))
            elif request_type.upper() == 'DELETE':
                response = self._session.delete(url=url, auth=auth, headers=headers, data=json.dumps(data))
        else:
            logger.warning(f'SNClient.enable_push_changes is set to False. [POST, PUT, DELETE] requests will not be executed.')
            return {}

        # GET request with a "202: no content" response:
        if response.status_code == 202:
            sn_error = {'error': {'message': 'No content returned', 'type': 'ServiceNow',
                                  'detail': f'Unexpected empty content in response for GET request: {response.request.url}'}}
            raise SNEmptyContent(req_error=None, sn_error=sn_error)

        # Check for HTTP error codes
        try:
            response.raise_for_status()
        except requests.RequestException as req_error:
            if 'error' in response.json():
                sn_error = response.json()
                raise SNException(req_error=req_error, sn_error=sn_error)
            elif 'result' in response.json():
                sn_error = response.json().get('result', {})
                raise SNException(req_error=req_error, sn_error=sn_error)

        result = response.json().get('result', {})
        return result

    def get_table_records(self, table_name, query=None, fields=None, display_value='false', limit=10):
        """
        Retrieve records from a ServiceNow table using the specified parameters.

        Args:
            table_name (str): The name of the ServiceNow table from which to retrieve records.
            query (str, optional): A query string to filter the records to retrieve.
            fields (str, optional): A comma-separated list of fields to include in the retrieved records.
            display_value (str): Return field display values ('true'), actual values ('false'), or both ('all').
                Options: ['true', 'false', 'all']
                Default: 'false'
            limit (int, optional): The maximum number of records to retrieve (default is 10).

        Returns:
            dict: The API response containing the retrieved records.

        This function retrieves records from a specified ServiceNow table using the provided parameters.
        It constructs the appropriate URL for the API request based on the table name, query, fields, and limit.
        """

        url = f"{table_name}?"

        if query:
            url += f"sysparm_query={query}&"

        if fields:
            url += f"sysparm_fields={fields}&"

        url += f"sysparm_display_value={display_value}&"

        url += f"sysparm_limit={limit}"

        full_url = self.get_table_api_url() + url
        return self._request(request_type='GET', url=full_url)

    def get_table_record(self, table_name, sys_id, fields=None, display_value='false'):
        """
        Retrieve a single record from a ServiceNow table by its sys_id.

        Args:
            table_name (str): The name of the ServiceNow table from which to retrieve the record.
            sys_id (str): The sys_id of the record to retrieve.
            fields (str, optional): A comma-separated list of fields to include in the retrieved records.
            display_value (str): Return field display values ('true'), actual values ('false'), or both ('all').
                Options: ['true', 'false', 'all']
                Default: 'false'

        Returns:
            dict: The API response containing the retrieved record.

        This method retrieves a single record from a specified ServiceNow table using its unique sys_id.
        It constructs the appropriate URL for the API request based on the table name and sys_id.

        Example usage:
        ```
        sn_client = ServiceNowAPIClient()
        table_name = 'incident'
        sys_id_to_retrieve = '1234567890abcdef1234567890abcdef'
        record = sn_client.get_table_record(table_name, sys_id_to_retrieve)
        print(record)
        ```
        """
        url = f'{table_name}/{sys_id}?'

        if fields:
            url += f"sysparm_fields={fields}&"

        url += f"sysparm_display_value={display_value}"

        full_url = self.get_table_api_url() + url
        return self._request(request_type='GET', url=full_url)

    def put_table_record(self, table_name, sys_id, data, fields=None, display_value='false'):
        """
        Update a record in a ServiceNow table using a PUT request.

        Args:
            table_name (str): The name of the ServiceNow table in which to update the record.
            sys_id (str): The sys_id of the record to update.
            data (dict): The data to update the record with, in JSON format.
            fields (str, optional): A comma-separated list of fields to include in the retrieved records.
            display_value (str): Return field display values ('true'), actual values ('false'), or both ('all').
                Options: ['true', 'false', 'all']
                Default: 'false'

        Returns:
            dict: The API response confirming the successful update.

        This method updates an existing record in a specified ServiceNow table using a PUT request.
        It constructs the appropriate URL for the API request based on the table name and sys_id.

        Example usage:
        ```
        sn_client = ServiceNowAPIClient()
        table_name = 'incident'
        sys_id_to_update = '1234567890abcdef1234567890abcdef'
        update_data = {"short_description": "Updated description"}
        response = sn_client.put_table_record(table_name, sys_id_to_update, data=update_data)
        print(response)
        ```
        """
        url = f'{table_name}/{sys_id}?'

        if fields:
            url += f"sysparm_fields={fields}&"

        url += f"sysparm_display_value={display_value}"

        full_url = self.get_table_api_url() + url
        return self._request(request_type='PUT', url=full_url, data=data)

    def post_table_record(self, table_name, data, fields=None, display_value='false'):
        """
        Create a new record in a ServiceNow table using a POST request.

        Args:
            table_name (str): The name of the ServiceNow table in which to create the record.
            data (dict): The data to create the new record with, in JSON format.
            fields (str, optional): A comma-separated list of fields to include in the retrieved records.
            display_value (str): Return field display values ('true'), actual values ('false'), or both ('all').
                Options: ['true', 'false', 'all']
                Default: 'false'

        Returns:
            dict: The API response containing the newly created record details.

        This method creates a new record in a specified ServiceNow table using a POST request.
        It constructs the appropriate URL for the API request based on the table name.
        """

        url = f"{table_name}?"

        if fields:
            url += f"sysparm_fields={fields}&"

        url += f"sysparm_display_value={display_value}"

        full_url = self.get_table_api_url() + url
        return self._request(request_type='POST', url=full_url, data=data)

    def call_api_now(self, request_type: str, url: str, data=None):
        """
        Execute an API request in the ServiceNow namespace using the specified parameters.

        Args:
            request_type (str): The type of HTTP request to execute ('GET', 'POST', 'PUT', 'DELETE').
            url (str): The relative URL for the API request within the 'api/now' namespace.
            data (dict, optional): Data to be included in the request, in JSON format.

        Returns:
            dict: The API response containing the result of the request.

        This method performs an HTTP request to a ServiceNow API endpoint within the 'api/now' namespace
        using the provided request type, relative URL, and optional data.

        Example usage:
        ```
        sn_client = ServiceNowAPIClient()
        api_url = 'table/incident'
        request_data = {"key": "value"}
        response = sn_client.call_api_now("POST", api_url, data=request_data)
        print(response)
        ```
        """
        if data is None:
            data = {}

        full_url = self._base_url + f'/api/now/{url}'
        return self._request(request_type=request_type, url=full_url, data=data)
