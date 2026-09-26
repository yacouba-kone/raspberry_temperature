import yaml
from azure.storage.blob import BlobServiceClient

with open("conf/base/credentials.yml", "r", encoding="utf-8") as f:
    credentials = yaml.safe_load(f)

config = credentials["azure_storage"]

client = BlobServiceClient.from_connection_string(
    config["connection_string"]
)

container = client.get_container_client(config["container_name"])

print("Connexion Azure OK")
print("Container :", container.container_name)

print("Blobs présents :")
for blob in container.list_blobs():
    print(" -", blob.name)