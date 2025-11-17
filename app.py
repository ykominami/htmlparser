from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from env import Env
from info import Info
from util import Util
from progress import Progress

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
        
    def _parse_html_file(self, file_path: Path) -> Optional[BeautifulSoup]:
        """
        Reads an HTML file and parses it into a BeautifulSoup object.

        This is a helper function that handles file reading and parsing.
        It returns a 'soup' object on success or None if the file is not found.

        Args:
            file_path: The path to the HTML file.

        Returns:
            A BeautifulSoup object if the file is parsed successfully, otherwise None.
        """
        try:
            with file_path.open('r', encoding='utf-8') as f:
                # Create a BeautifulSoup object using the lxml parser
                # soup = BeautifulSoup(f, 'lxml')
                soup = BeautifulSoup(f, 'html5lib')
                return soup
        except FileNotFoundError:
            print(f"Error: The file at {file_path} was not found.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def process_for_udemy(self, info: Info) -> List[Dict[str, str]]:
        print('process_for_udemy')
        soup = info.soup
        append_count = 0
        no_append_count = 0
        """divの処理"""
        for div_tag in soup.find_all('div', {'class': 'enrolled-course-card--container--WJYo9'}):
        # for div_tag in soup.find_all('div', {'class': 'course-card-title-module--title--W49Ap'}):
            # print(f'div_tag={div_tag}')
            a_tag = div_tag.find('a')
            if a_tag is None:
                continue
            url = a_tag.get('href', '#')
            text = a_tag.get_text(strip=True)
            course_id = self.get_course_id_from_url(url)

            instructors = self.get_instructors(div_tag)
            progress = self.get_progress(div_tag)

            # Extract course_id from URL parameters

            result = self.add_list_and_assoc(url=url, text=text, course_id=course_id, instructors=instructors, progress=progress)
            if result:
                append_count += 1
            else:
                no_append_count += 1

        info.append_count = append_count
        info.no_append_count = no_append_count
        self.append_count += append_count
        self.no_append_count += no_append_count

        return self.links_list


    def get_progress(self, div_tag: BeautifulSoup) -> Progress:
        # meter_div = div_tag.find('div', {'data-purpose': 'meter'})
        meter_div = div_tag.find('div', {'class': 'ud-meter meter-module--meter--9-BwT'})
        
        meter = ['_0_']
        meter_str = ''
        valuemin = '0'
        valuemax = '100'
        valuenow = '0'
        meter = f'{valuemin}-{valuemax}-{valuenow}'
        if meter_div is not None:
            # meter = meter_div.get_text(strip=True)
            meter_str = meter_div.get('aria-label', '')
            valuemin = meter_div.get('aria-valuemin', '0')
            valuemax = meter_div.get('aria-valuemax', '100')
            valuenow = meter_div.get('aria-valuenow', '0')
        else:
            print(f'#### meter2={meter}')

        progress = Progress(meter_str=meter_str, valuemin=valuemin, valuemax=valuemax, valuenow=valuenow)
        return progress

    def get_instructors(self, div_tag) -> list[str]:
        instructors = ['_0_']
        child_div = div_tag.find('div', {'data-purpose': 'safely-set-inner-html:course-card:visible-instructors'})
        if child_div is not None:
            instructors = child_div.get_text(strip=True)
            print(f'#### instructors1={instructors}')
        else:
            print(f'#### instructors2={instructors}')
        return instructors

    def process_for_h3(self, info: Info) -> List[Dict[str, str]]:
        print('process_for_h3')
        soup = info.soup
        append_count = 0
        no_append_count = 0
        """H3モードの処理"""
        for h3_tag in soup.find_all('h3'):
            # print(f'h3_tag={h3_tag}')
            a_tag = h3_tag.find('a')
            if a_tag is None:
                continue
            url = a_tag.get('href', '#')
            text = a_tag.get_text(strip=True)

            # h3タグの子要素であるdiv要素のうち、属性data-purposeの値が"safely-set-inner-html:course-card:visible-instructors"であるものを取得
            child_div = h3_tag.find('div', {'data-purpose': 'safely-set-inner-html:course-card:visible-instructors'})
            
            # child_divのすべての階層のテキストを取り出して、変数instructorsに代入
            instructors = ['_0_']
            if child_div is not None:
                instructors = child_div.get_text(strip=True)
                print(f'#### instructors1={instructors}')
            else:
                print(f'#### instructors2={instructors}')

            # Extract course_id from URL parameters
            course_id = self.get_course_id_from_url(url)
            result = self.add_list_and_assoc(url=url, text=text, course_id=course_id, instructors=instructors)
            if result:
                append_count += 1
            else:
                no_append_count += 1

        info.append_count = append_count
        info.no_append_count = no_append_count
        self.append_count += append_count
        self.no_append_count += no_append_count

        return self.links_list

    def add_list_and_assoc(self, url: str, text: str, course_id: str, instructors: list[str], progress: Progress = '') -> bool:
        result = False
        if not course_id in self.links_assoc.keys():
            if instructors is not None:
                # instructors = instructors.split(',')
                print(f'#### add_list_and_assoc instructors={instructors}')
                record = self.make_record(url=url, text=text, course_id=course_id, instructors=instructors, progress=progress)
                # record = self.make_record(url, text, course_id)
                print(f'=1 record1={record}')
            else:
                record = self.make_record(url=url, text=text, course_id=course_id, instructors=instructors, progress=progress)
                print(f'==2 record2={record}')

            self.links_assoc[course_id] = record
            self.links_list.append(record)
            result = True
        else:
            pass

        return result

    def make_record(self, url: str, text: str, course_id: str, instructors: list[str], progress: Progress | dict) -> Dict[str, str]:
        if isinstance(progress, dict):
            progress_dict = progress
        else:
            progress_dict = progress.to_dict()
        print(f'############ make_record instructors={instructors}')
        print(f'############ make_record progress_yml={progress_dict}')
        """レコードを作成する"""
        # URI形式のチェック
        parsed = urlparse(url)
        if not parsed.scheme:
            raise ValueError(f"URL '{url}' is not a valid URI: missing scheme")
        if not parsed.netloc and not parsed.path and not parsed.fragment:
            raise ValueError(f"URL '{url}' is not a valid URI: missing authority, path, or fragment")
        # progress_yml = progress.to_yml()
        record = {'URL': url, 'Text': text, 'Course_ID': course_id, 'Instructors': instructors, 'Progress': progress_dict}
        # print(f'0 record0={record}')
        return record

    def get_course_id_from_url(self, url: str) -> str:
        if url and url != '#':
            try:
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                course_id = query_params.get('course_id', [''])[0]
            except Exception:
                course_id = ''

        return course_id

    def process_for_a(self, info: Info) -> List[Dict[str, str]]:
        """aモードの処理"""
        print('process_for_a')
        soup = info.soup
        for a_tag in soup.find_all('a'):
            # classが"a-link-normal"でない場合はcontinue
            if a_tag.get('class') != ['a-link-normal']:
                print(f'a_tag.get("class")={a_tag.get("class")}')
                continue
            # print(f'a_tag.get("class")={a_tag.get("class")}')
            # classが"a-link-normal"の場合、anchorタグの子要素のimgタグのalt属性を取得
            url = a_tag.get('href', '#')
            # print(f'url={url}') 
            img_tag = a_tag.find('img')
            # print(f'img_tag={img_tag}')
            if img_tag:
                text = img_tag.get('alt', '')
            else:
                text = a_tag.get_text(strip=True)
            # Extract course_id from URL parameters
            course_id = self.get_course_id_from_url(url)
            instructors={'-'}
            result = self.add_list_and_assoc(url=url, text=text, course_id=course_id, instructors=instructors)
            if result:
                append_count += 1
            else:
                no_append_count += 1

        info.append_count = append_count
        info.no_append_count = no_append_count
        self.append_count += append_count
        self.no_append_count += no_append_count

        return self.links_list

    def process_for_ku(self, info: Info) -> List[Dict[str, str]]:
        print('process_for_ku')
        soup = info.soup
        for a_tag in soup.find_all('a'):
            # classが"a-link-normal"でない場合はcontinue
            if a_tag.get('class') != ['a-link-normal']:
                print(f'a_tag.get("class")={a_tag.get("class")}')
                continue    
            url = a_tag.get('href', '#')
            text = a_tag.get_text(strip=True)
            course_id = self.get_course_id_from_url(url)
            instructors={'-'}
            result = self.add_list_and_assoc(url=url, text=text, course_id=course_id, instructors=instructors)
            if result:
                append_count += 1
            else:
                no_append_count += 1

        info.append_count = append_count
        info.no_append_count = no_append_count
        self.append_count += append_count
        self.no_append_count += no_append_count

        return self.links_list

    def _extract_links_from_info(self, info: Info) -> List[Dict[str, str]]:
        """
        Extracts all links and their anchor text from a BeautifulSoup object.

        This helper function iterates through all anchor (<a>) tags found in the soup
        and extracts the 'href' attribute and the tag's text content.

        Args:
            soup: The BeautifulSoup object to extract links from.

        Returns:
            A list of dictionaries, where each dictionary represents a link
            with 'url', 'text', and 'course_id' keys.
        """
        if info.mode == "udemy":
            links_list = self.process_for_udemy(info)
        elif info.mode == "h3":
            links_list = self.process_for_h3(info)
        elif info.mode == "a":
            links_list = self.process_for_a(info)
        elif info.mode == "status":
            # links_list = self.find_status_span_ancestors(info['soup'])
            status_spans = info['soup'].find_all('span', role='status')
            print(f'len( status_spans )={len(status_spans)}')
            # exit(0)
            links_list = self.find_item_ancestors(status_spans)
        elif info.mode == "ku":
            print('process_for_ku')
            links_list = self.process_for_ku(info)
        else:
            links_list = []

        return links_list

    def get_links_from_html(self, file_path: Path, mode: str) -> List[Dict[str, str]]:
        """
        Parses an HTML file and returns a list of all links and their text.

        This is the main function that orchestrates the parsing and extraction process.
        It handles the overall workflow from file path to the final list of links.

        Args:
            file_path: The path to the HTML file.

        Returns:
            A list of dictionaries containing the links, or an empty list if
            an error occurs or no links are found.
        """
        print(f'get_links_from_html file_path.name={file_path.name} mode={mode}')
        links = []
        if not file_path in self.info.keys():
            soup = self._parse_html_file(file_path)
            # print(f'soup={soup}')
            if soup:
                info = Info(mode, file_path, file_path.name, soup, 0, 0)
                self.info[file_path.name] = info
                links = self._extract_links_from_info(info)
        # print(f'soup={soup}')
        return links

    def get_link_array(self, extracted_links: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """抽出されたリンクを配列形式に変換する"""
        return [self.make_record(link['URL'], link['Text'], link['Course_ID'], link['Instructors'], link['Progress']) for link in extracted_links]

    def loop(self, files: List[Path], mode: str):
        array = []
        for file in files:
            print(f'file={file}')
            extracted_links = self.get_links_from_html(file, mode)
            if extracted_links:
                print(f"Found {len(extracted_links)} links in '{file}':\n")
                arrayx = self.get_link_array(extracted_links)
                if len(arrayx) > 0:
                    array.append(arrayx)
        return array

    def output_link_assoc_in_yaml(self, output_path: Path = None) -> str:
        self.output_yaml(self.links_assoc, output_path)

    def output_yaml(self, assoc: dict, output_path: Path = None) -> str:
        return Util.output_yaml(self.links_assoc, output_path)

    def run(self, env: Env):
        path_array = env.get_files()
        mode = env.mode()
 
        """アプリケーションのメイン実行メソッド"""
        list = self.loop(path_array, mode)

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
    env = Env('config.yaml')
    # env.set_pattern('Udemy-1-file')
    # list = ['Udemy-1-file', 'Udemy-1-dir', 'Udemy-2-file', 'Udemy-2-dir', 'Udemy-3-file', 'Udemy-3-dir']
    # list = ['Udemy-1-file']
    # patterns = ['Udemy-3-file']
    patterns = ['Amazon-KU-1-file']
    app = App()
    for pattern in patterns:
        env.set_pattern(pattern)
        app.run(env)

    # output_path = Path('output_2.yaml')
    output_path = Path('output_10.yaml')
    Util.output_yaml(app.links_assoc, output_path)
    # app.output_link_assoc_in_yaml(Path('output_1.yaml'))
