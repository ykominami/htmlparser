from udemyscraper import UdemyScraper
from info import Info
from typing import List, Dict, Optional

class AScraper(UdemyScraper):
  def __init__(self):
    super().__init__()

  def scrape(self, info: Info) -> List[Dict[str, str]]:
    print('ascraper scrape')
    soup = info.soup
    append_count = 0
    no_append_count = 0
    """ aタグでは部分的な情報しか取得できない """
    """ クラスが"a-link-normal"でない場合はcontinue """
    """aの処理"""
    for a_tag in soup.find_all('a'):
        # print(f'a_tag={a_tag}')

        # classが"a-link-normal"でない場合はcontinue
        if a_tag.get('class') != ['a-link-normal']:
            # print(f'continue a_tag.get("class")={a_tag.get("class")}')
            continue
        print(f'Not continuea_tag.get("class")={a_tag.get("class")}')
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


  def _extract_links_from_info(self,info: Info) -> List[Dict[str, str]]:
    super()._extract_links_from_info(info)
    links_list = self.scrape(info)

    return links_list
