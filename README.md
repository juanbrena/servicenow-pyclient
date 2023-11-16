# servicenow-pyclient
A ServiceNow REST API python client
<br>
Requires [requests](http://docs.python-requests.org/en/master/)


### About
[ServiceNow](https://www.servicenow.com) is an IT service management (ITSM) vendor with a solid rest API.
<br>
You can search for your specific ServiceNow instance API docs [here](https://docs.servicenow.com).


### Instantiate a ServiceNow REST API client
```python
from servicenow_pyclient import SNClient
sn_client = SNClient(url='<YOUR SN INSTANCE URL>', username='<YOUR USERNAME>', password='<YOUR PASSWORD>')
```

### Get a record from a table with the sys_id
```python
record = sn_client.get_table_record(table_name='TABLE_NAME', sys_id='1234567890')
```