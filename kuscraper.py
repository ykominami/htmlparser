from scraper import Scraper
from info import Info
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from pathlib import Path

class KUScraper(Scraper):
  def __init__(self):
    super().__init__()

  def scrape(self, info: Info) -> List[Dict[str, str]]:
    print('kuscraper scrape')
    soup = info.soup
    append_count = 0
    no_append_count = 0
    """aの処理"""
    for a_tag in soup.find_all('a'):
        # classが"a-link-normal"でない場合はcontinue
        if a_tag.get('class') != ['a-link-normal']:
            print(f'a_tag.get("class")={a_tag.get("class")}')
            continue

    return self.links_list


