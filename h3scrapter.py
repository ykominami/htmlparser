from udemyscraper import UdemyScraper
from info import Info
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

class H3Scraper(UdemyScraper):
  def __init__(self):
    super().__init__()

  def scrape(self, info: Info) -> List[Dict[str, str]]:
    print('h3scraper scrape')
    soup = info.soup
    append_count = 0
    no_append_count = 0
    """h3では部分的にしか取得できない"""
    
    """h3の処理"""
    for h3_tag in soup.find_all('h3'):
        print(f'h3_tag={h3_tag}')
        '''
        # h3タグの子要素であるa要素を取得
        a_tag = h3_tag.find('a')
        if a_tag is None:
            continue
        url = a_tag.get('href', '#')
        text = a_tag.get_text(strip=True)

        # Extract course_id from URL parameters
        course_id = self.get_course_id_from_url(url)
        '''

        # h3タグの子要素であるdiv要素のうち、属性data-purposeの値が"safely-set-inner-html:course-card:visible-instructors"であるものを取得
        child_div = h3_tag.find('div', {'data-purpose': 'safely-set-inner-html:course-card:visible-instructors'})
        if child_div is None:
            raise ValueError(f'child_div is None')
        
        # child_divのすべての階層のテキストを取り出して、変数instructorsに代入
        instructors = ['_0_']

        instructors = child_div.get_text(strip=True)
        print(f'#### instructors1={instructors}')
        progress = self.get_progress(child_div)
      


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

  def _extract_links_from_info(self, info: Info) -> List[Dict[str, str]]:
    super()._extract_links_from_info(info)
    links_list = self.scrape(info)
    return links_list
