from bs4.element import NavigableString
from yklibpy.common.info import Info
from yklibpy.common.util import Util
from yklibpy.htmlparser.scraper import Scraper


class WorkInfo:
    def __init__(
        self,
        asin: str,
        target: str,
        url: str,
        title: str,
        sequence: int,
    ):
        self.asin = asin
        self.target = target
        self.url = url
        self.title = title
        self.sequence = sequence

        result = Util.is_valid_urls([url])
        if result:
            self.url = url
        else:
            self.url = ""

    def to_assoc(self):
        assoc = Scraper._to_assoc(self.title, self.url, self.sequence)
        assoc["asin"] = self.asin
        assoc["target"] = self.target
        return assoc


class AmazonSavedCartScraper(Scraper):
    def __init__(self, sequence: int):
        """Initialize Udemy-specific scraper state.

        Returns:
          None
        """
        super().__init__(sequence)

    def scrape(self, info: Info) -> None:
        """Extract Udemy dashboard cards and convert them into records.

        Args:
          info (Info): Parsed HTML container and counters for the current file.

        Returns:
          List[Dict[str, str]]: List of record dictionaries appended this run.
        """
        print("amazonsavedcart scrape")
        soup = info.soup
        append_count = 0
        no_append_count = 0
        """divの処理"""
        print("--- 子要素の列挙 ---")

        for div_tag in soup.find_all("div", {"id": "sc-saved-cart-items"}):
            # print(div_tag)
            list = div_tag.find_all("div", {"data-asin": True})
            # print(list)
            for div_tag_2 in list:
                # print(f'div_tag_2={div_tag_2}')
                asin = div_tag_2.get("data-asin", "")
                # print(f'asin={asin}')
                div_tag_3 = div_tag_2.find("div", {"class": "sc-list-item-removed-msg"})
                # print(f"div_tag_3={div_tag_3}")
                if div_tag_3 is not None:
                    a_tag = div_tag_2.find("a")
                    if a_tag is None:
                        continue
                    url = a_tag.get("href", "#")
                    title = "".join(
                        s for s in a_tag.contents if isinstance(s, NavigableString)
                    ).strip()
                    if not isinstance(title, str):
                        title = ""
                    if not isinstance(asin, str):
                        asin = ""
                    if not isinstance(url, str):
                        url = ""

                    work_info = WorkInfo(
                        asin=asin,
                        target="savedcart",
                        url=url,
                        title=title,
                        sequence=self.sequence,
                    )
                    result = self.add_assoc(work_info)

                    if result:
                        append_count += 1
                    else:
                        no_append_count += 1

        print("--- 子要素の列挙終了 ---")

        info.append_count = append_count
        info.no_append_count = no_append_count
        self.append_count += append_count
        self.no_append_count += no_append_count
        print(
            f"###############   amazonsavedcart scrape len( self.links_assoc )={len(self.links_assoc)}"
        )
        return None

    def add_assoc(self, work_info: WorkInfo) -> bool:
        Scraper._add_assoc(
            self.links_assoc, work_info.asin, work_info.sequence, work_info.to_assoc()
        )
        return True
