import yaml
import os
PY_ENV = os.getenv("PY_ENV", "local")
if PY_ENV == "local":
    ROOT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(f"{ROOT_DIRECTORY}/conf/base/credentials.yml", 'rb') as f:
        yaml_config = yaml.safe_load(f)
    workers_queue_conf = yaml_config['dev-azure']['workers_queue']['SERVICE_BUS']
    # Retrieving the params
    policy_name_ = workers_queue_conf['POLICY_NAME']
    primary_key_ = workers_queue_conf['PRIMARY_KEY']
    namespace_ = workers_queue_conf['NAMESPACE']
    type_ = workers_queue_conf['TYPE']
    # Constructing the broker connection string
    service_bus_broker = f"{type_}://{policy_name_}:{primary_key_}@{namespace_}"

else:
    # Retrieving the params
    policy_name_ = os.getenv('ASBUS_POLICY_NAME')
    primary_key_ = os.getenv('ASBUS_PRIMARY_KEY')
    namespace_ = os.getenv('ASBUS_NAMESPACE')
    type_ = 'azureservicebus'
    # Constructing the broker connection string
    service_bus_broker = f"{type_}://{policy_name_}:{primary_key_}@{namespace_}"