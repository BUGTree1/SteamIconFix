from typing import Any, NoReturn
from sys import exit
from steam.client import SteamClient

def error(msg: str) -> NoReturn:
    print(f"ERROR: {msg}")
    exit(1)

client: SteamClient = SteamClient()

appid: int = 730

product_info: dict[Any, Any] | None = client.get_product_info([appid], [], False, False, False)

if product_info is None:
    error("Product info is none")
