from configparser import ConfigParser
from steam.client import SteamClient
from typing import Any, NoReturn
from pathlib import Path
import urllib.request
from sys import exit
import configparser
import http.client
import subprocess
import re
import os

client: SteamClient = SteamClient()

desktop_dir: Path = Path('~/Desktop').expanduser()
icon_dir: Path = Path('~/.local/share/icons/hicolor/64x64/apps/').expanduser()

def error(msg: str) -> NoReturn:
    print(f"ERROR: {msg}")
    exit(1)
    
def warning(msg: str) -> None:
    print(f"WARNING: {msg}")
    
def get_largest_ico_index(ico_path: Path) -> int:
    result = subprocess.run([f'magick identify "{ico_path}"'], shell=True, capture_output=True, text=True, check=True)
    
    largest_index = 0
    largest_area = 0

    pattern = re.compile(r'\[(\d+)\].*?(\d+)x(\d+)')

    for line in result.stdout.splitlines():
        match = pattern.search(line)
        if match:
            index = int(match.group(1))
            width = int(match.group(2))
            height = int(match.group(3))
            area = width * height
            if area > largest_area:
                largest_area = area
                largest_index = index

    return largest_index

def download_icon(appid: int) -> None:
    product_info = client.get_product_info(apps=[appid])

    if product_info == None:
        error("Product info is none")
        
    if product_info['apps'][appid]['_missing_token']:
        tokens = client.get_access_tokens(app_ids=[appid])
        result = client.get_product_info(apps=[{'appid': appid,'access_token': tokens['apps'][appid]}])  # type: ignore
        
    if not 'clienticon' in product_info['apps'][appid]['common']:
        warning(f'No icon string found for appid: {appid}!')
    else:
        icon_string = product_info['apps'][appid]['common']['clienticon']
        
        icon_url = f"https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/{appid}/{icon_string}.ico"

        # TODO: Also download linuxclient zip to ~/.steam/steam/steam/games

        icon_path = icon_dir.joinpath(f'steam_icon_{appid}.ico')
        icon_path_png = icon_path.with_suffix('.png')

        icon: http.client.HTTPResponse = urllib.request.urlopen(icon_url)
        icon_file = open(icon_path,'b+w')
        icon_file.write(icon.read())
        icon_file.close()
        icon.close()
        
        ico_idx: int = get_largest_ico_index(icon_path)
        code = subprocess.run([f'magick "{icon_path}[{ico_idx}]" "{icon_path_png}"'], shell=True, cwd=icon_dir)
        if code.returncode != 0:
            error(f'ImageMagick returned {code.returncode}!')
        
        os.remove(icon_path)
        
        print(f"Icon for appid: {appid} downloaded succesfully!")

def parse_shorcut(file: Path):
    parser: ConfigParser = configparser.ConfigParser()
    parser.optionxform = str # type: ignore
    parser.read(file)
    if 'Exec' in parser['Desktop Entry']:
        exec_str = parser.get('Desktop Entry', 'Exec', raw=True)
        appid_match = re.match(r'.*steam://rungameid/(.*)', exec_str)
        if appid_match != None:
            appid = appid_match.group(1)
            print(f'Found appid: {appid} in shortcut: {file}!')
            download_icon(int(appid))
            
            parser.set('Desktop Entry', 'Icon', f'steam_icon_{appid}')
            file_stream = open(file, 'w+')
            parser.write(file_stream, space_around_delimiters=False)
            file_stream.close()

def main():
    client.anonymous_login()

    for filename in os.listdir(desktop_dir):
        file: Path = desktop_dir.joinpath(filename)
        if file.suffix == '.desktop':
            parse_shorcut(file)

    #download_icon(730)

if __name__ == '__main__':
    main()