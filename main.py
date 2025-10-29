from typing import Any, NoReturn
from sys import exit
from steam.client import SteamClient

def error(msg: str) -> NoReturn:
    print(f"ERROR: {msg}")
    exit(1)

client: SteamClient = SteamClient()
client.anonymous_login()

appid: int = 730

product_info = client.get_product_info(apps=[appid])

if product_info is None:
    error("Product info is none")
    
if product_info['apps'][appid]['_missing_token']:
    tokens = client.get_access_tokens(app_ids=[appid])
    result = client.get_product_info(apps=[{'appid': appid,'access_token': tokens['apps'][appid]}])

if product_info['apps'][appid]['common']['linuxclienticon']:
    icon_string = product_info['apps'][appid]['common']['linuxclienticon']
else:
    icon_string = product_info['apps'][appid]['common']['clienticon']

if not icon_string:
    error('No icon string found!')
    
print(icon_string)

# TODO: download icon from cloudflare