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
        """Initialize the application state and prepare storage for results.

        Returns:
            None
        """
        self._setup()
    
    def _setup(self):
        """Reset link buffers, metadata, and counters for a fresh run.

        Returns:
            None
        """
        self.links_list = []
        self.links_assoc = {}
        self.info = {}
        self.append_count = 0
        self.no_append_count = 0
        
    def create_scraper(self, mode: str) -> Scraper:
        """Build the appropriate scraper implementation for the requested mode.

        Args:
            mode (str): Logical identifier such as ``"udemy"`` or ``"h3"``.

        Returns:
            Scraper: Concrete scraper that knows how to parse the given site, or
            ``None`` when the mode is unsupported.
        """
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
        """Iterate through HTML files and accumulate extracted link metadata.

        Args:
            files (List[Path]): Collection of HTML paths to inspect.
            mode (str): Scraper mode passed through to :meth:`create_scraper`.

        Returns:
            dict: Mapping of link identifiers to their structured attributes.
        """
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
        """Persist the in-memory link dictionary as a YAML document.

        Args:
            output_path (Path | None): Destination file. When ``None`` the YAML
                string is simply returned.

        Returns:
            str: YAML dump created by :meth:`output_yaml`.
        """
        return self.output_yaml(self.links_assoc, output_path)

    def output_yaml(self, assoc: dict, output_path: Path = None) -> str:
        """Serialize the provided mapping into YAML and optionally save it.

        Args:
            assoc (dict): Data to convert into YAML.
            output_path (Path | None): Optional destination file.

        Returns:
            str: YAML string produced by :class:`Util`.
        """
        return Util.output_yaml(assoc, output_path)

    def run(self, env: Env):
        """Fetch file paths from the environment and scrape each one.

        Args:
            env (Env): Environment descriptor that supplies file lists and mode.

        Returns:
            None
        """
        path_array = env.get_files()
        mode = env.mode()
 
        assoc = self.loop(path_array, mode)
        print(f'app.py run len( assoc )={ len(assoc) }')
        # self.links_assoc = self.links_assoc.update(list)
        self.links_assoc.update(assoc)
        print(f'app.py run len( self.links_assoc )={ len(self.links_assoc) }')

    def find_item_ancestors(self, items: List[Dict[str, any]]):
        """Traverse ancestor chains for the supplied elements and log details.

        Args:
            items (List[Dict[str, any]]): Result set (e.g., BeautifulSoup nodes)
                whose parent hierarchy should be inspected.

        Returns:
            list: Currently an empty list placeholder for future aggregation.
        """
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
        """Locate role=\"status\" spans and dump their ancestor structure.

        Args:
            soup (BeautifulSoup): Parsed HTML document.

        Returns:
            list: Result from :meth:`find_item_ancestors`.
        """
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
        print(f'app.py main pattern={pattern}')
        ret = env.set_pattern(pattern)
        if ret == None:
            print(f'Not found pattern={pattern}')
            exit(0)
        app.run(env)

    output_path = Path(output_file)
    print(f'output_path={output_path} len( app.links_assoc )={ len(app.links_assoc) }   ' )

    Util.output_yaml(app.links_assoc, output_path)
