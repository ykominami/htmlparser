from bs4 import BeautifulSoup
from typing import List, Dict
# import os
import sys
from pathlib import Path
# from urllib.parse import urlparse, parse_qs
from env import Env
from info import Info
from util import Util
#from progress import Progress
from udemyscraper import UdemyScraper
from kuscraper import KUScraper
from h3scrapter import H3Scraper
from ascrapter import AScraper
from scraper import Scraper

class App:
    """
    HTMLファイルからリンクを抽出するアプリケーションクラス
    """
    
    def __init__(self):
        """Appクラスの初期化"""
        self._setup()
    
    def _setup(self):
        """Appクラスの初期化"""
        self.links_list = []
        self.links_assoc = {}
        self.info = {}
        self.append_count = 0
        self.no_append_count = 0
        
    def create_scraper(self, mode: str) -> Scraper:
        if mode == "udemy":
            return UdemyScraper()
            # return H3Scraper()
            # return AScraper()
        elif mode == "h3":
            return H3Scraper()
        elif mode == "a":
            return AScraper()
        elif mode == "ku":
            return KUScraper()
        else:
            return None

    def loop(self, files: List[Path], mode: str):
        assoc = {}
        for file in files:
            print(f'file={file}')
            scraper = self.create_scraper(mode)
            extracted_links_assoc = scraper.get_links_assoc_from_html(file)
            if extracted_links_assoc:
                # print(f"app.py loop Found {len(extracted_links_assoc)} links in '{file}':\n")
                # arrayx = scraper.get_link_array(extracted_links)
                # print(f'app.py loop len(arrayx)={len(arrayx)}')
                if len(extracted_links_assoc) > 0:
                    print(f'run len( extracted_links_assoc )={ len(extracted_links_assoc) }')
                    assoc.update(extracted_links_assoc)
        print(f'app.pyloop TOTAL len( assoc )={ len(assoc) }')
        return assoc

    def output_link_assoc_in_yaml(self, output_path: Path = None) -> str:
        self.output_yaml(self.links_assoc, output_path)

    def output_yaml(self, assoc: dict, output_path: Path = None) -> str:
        return Util.output_yaml(self.links_assoc, output_path)

    def run(self, env: Env):
        path_array = env.get_files()
        mode = env.mode()
 
        """アプリケーションのメイン実行メソッド"""
        assoc = self.loop(path_array, mode)
        print(f'app.py run len( assoc )={ len(assoc) }')
        # self.links_assoc = self.links_assoc.update(list)
        self.links_assoc.update(assoc)
        print(f'app.py run len( self.links_assoc )={ len(self.links_assoc) }')

    def find_item_ancestors(self, items: List[Dict[str, any]]):
        for i, item in enumerate(items, 1):
            print(f"Status Span {i}: {item.get_text(strip=True)}")
            
            # 祖先要素をすべて取得
            ancestors = []
            current = item.parent
            level = 1
            
            while current and current.name != 'html':
                assoc = {
                    'level': level,
                    'tag': current.name,
                    'text': current.get_text(strip=True)[:100] + "..." if len(current.get_text(strip=True)) > 100 else current.get_text(strip=True),
                    'class': current.get('class', []),
                    'id': current.get('id', '')
                }
                ancestors.append(assoc)
                if 'item' in assoc['class']:
                    break

                current = current.parent
                level += 1
            
            for ancestor in ancestors:
                indent = "  " * ancestor['level']
                print(f"{indent}Level {ancestor['level']}: <{ancestor['tag']}>")
                print(f"{indent}  Text: {ancestor['text']}")
                print(f"{indent}  Class: {ancestor['class']}")
                print(f"{indent}  ID: {ancestor['id']}")
            
            print("-" * 50)

        return []

    def find_status_span_ancestors(self, soup: BeautifulSoup):
        """role="status"のspanタグの祖先要素をすべて取得する"""
        status_spans = soup.find_all('span', role='status')
        return self.find_item_ancestors(status_spans)

if __name__ == "__main__":
    cmd_file = sys.argv[1] if len(sys.argv) > 1 else 'cmd.yaml'
    cmd_file_path = Path(cmd_file)
    assoc = Util.load_yaml(cmd_file_path)
    config_file_path = Path(assoc['config_file'])
    env = Env(config_file_path)
    patterns = assoc['patterns'] if 'patterns' in assoc else ['Amazon-KU-1-file']
    output_file = assoc['output_file'] if 'output_file' in assoc else ['output_0.yaml']
    input_file = assoc['input_file'] if 'input_file' in assoc else None

    app = App()
    if input_file:
        input_file_path = Path(input_file)
        input_assoc = Util.load_yaml(input_file_path)
        app.links_assoc.update(input_assoc)

    for pattern in patterns:
        env.set_pattern(pattern)
        app.run(env)

    output_path = Path(output_file)
    print(f'output_path={output_path} len( app.links_assoc )={ len(app.links_assoc) }   ' )

    Util.output_yaml(app.links_assoc, output_path)
