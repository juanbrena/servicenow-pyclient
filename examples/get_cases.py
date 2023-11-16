from servicenow_pyclient import SNClient


def main():

    # Create ServiceNow Client
    sn_client = SNClient(url='<YOUR SN INSTANCE URL>',
                         username='<YOUR USERNAME>',
                         password='<YOUR PASSWORD>',
                         enable_push_changes=False)

    # Let's get 10 cases that are active
    query = 'active=true'
    cases = sn_client.get_table_records(table_name='TABLE_NAME', query=query, limit=10)

    for case in cases:
        print(f"{case}")


if __name__ == '__main__':
    main()
