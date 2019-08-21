from huawei_lte_api.Client import Client
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api.Connection import Connection
from pprint import pprint



connection = Connection('http://192.168.8.1/')
client = Client(connection)

pprint(client.device.signal())