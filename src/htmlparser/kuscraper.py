from typing import Any, Dict

from yklibpy.common.info import Info
from yklibpy.common.util import Util
from yklibpy.htmlparser.scraper import Scraper


class KUScraper(Scraper):
    class WorkInfo:
        def __init__(self, url: str, title: str, sequence: int):
            self.url: str = ""
            self.title: str = ""
            self.sequence: int = 0
            result = Util.is_valid_urls([url])
            if result:
                self.url = url
                self.title = title
                self.sequence = sequence

        def to_assoc(self):
            assoc = Scraper._to_assoc(self.title, self.url, self.sequence)
            return assoc

    def __init__(self, sequence: int):
        super().__init__(sequence)
        self.links_assoc: dict[str, dict[str, Any]] = {}

    def scrape(self, info: Info) -> Dict[str, Dict[str, Any]]:
        # <div id="itemsList" class="a-section a-spacing-top-large">
        #   <ul id="listContainer" class="a-unordered-list a-nostyle a-vertical" role="list">

        soup = info.soup
        """aの処理"""
        for div_tag in soup.find_all("div", {"id": "itemsList"}):
            for a_tag in div_tag.find_all("a"):
                if a_tag.get("class") != ["a-link-normal"]:
                    continue
                url = a_tag.get("href", "#")
                if isinstance(url, str):
                    url = url
                else:
                    url = ""

                img_tag = a_tag.find("img")
                if img_tag:
                    title = img_tag.get("alt", "")
                    if isinstance(title, str):
                        title = title
                    else:
                        title = ""
                else:
                    title = a_tag.get_text(strip=True)
                # print(f"text={text}")
                work_info = self.WorkInfo(url=url, title=title, sequence=self.sequence)
                self.add_assoc(work_info)
        return self.links_assoc

    def add_assoc(self, work_info: WorkInfo) -> bool:
        Scraper._add_assoc(
            self.links_assoc, work_info.url, work_info.sequence, work_info.to_assoc()
        )
        return True
