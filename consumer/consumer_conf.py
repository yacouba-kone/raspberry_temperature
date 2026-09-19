import yaml
import os

PY_ENV =  os.getenv('PY_ENV', 'local')

if PY_ENV == "local":
    ROOT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(f'{ROOT_DIRECTORY}/conf/base/credentials.yml', 'rb') as conf_file:
        conf = yaml.safe_load(conf_file)
        print(conf)
        conf_message_broker = conf['dev-azure']['message_broker']
    CONNECTION_STR = conf_message_broker['CONNECTION_STR']
    CONSUMER_GROUP= conf_message_broker['CONSUMER_GROUP']
    EVENT_HUB_NAME= conf_message_broker['EVENT_HUB_NAME']

else:
    CONNECTION_STR = os.getenv("CONSUMER_CONNECTION_STR")
    CONSUMER_GROUP = os.getenv("CONSUMER_GROUP")
    EVENT_HUB_NAME= os.getenv('CONSUMER_EVENT_HUB_NAME')

