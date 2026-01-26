from typing import Dict

from yklibpy.common.info import Info
from yklibpy.common.util import Util
from yklibpy.htmlparser.scraper import Scraper


class FanzaDoujinPurchasedScraper(Scraper):
    class WorkInfo:
        def __init__(
            self,
            target: str,
            product_id: str,
            url: str,
            purchased_date: str,
            kind: str,
            title: str,
            circle_name: str,
            sequence: int,
        ):
            self.target = target
            self.product_id = product_id
            self.url = url
            self.purchased_date = purchased_date
            self.kind = kind
            self.title = title
            self.circle_name = circle_name
            self.sequence = sequence

        def to_assoc(self):
            assoc = Scraper._to_assoc(self.title, self.url, self.sequence)
            assoc["product_id"] = self.product_id
            assoc["target"] = self.target
            assoc["purchased_date"] = self.purchased_date
            assoc["kind"] = self.kind
            assoc["circle_name"] = self.circle_name
            return assoc

    def __init__(self, sequence: int):
        super().__init__(sequence)

    def add_assoc(self, work_info: WorkInfo):
        product_id = Util.extract_product_id(work_info.url)
        result = Scraper._add_assoc(
            self.links_assoc, product_id, work_info.sequence, work_info.to_assoc()
        )
        print(
            f"result={result} product_id={product_id} url={work_info.url} len={len(self.links_assoc)}"
        )
        return result

    def scrape(self, info: Info) -> Dict[str, Dict[str, str]]:
        soup = info.soup
        append_count = 0
        no_append_count = 0
        target = "purchased"
        print("scrape============================")
        for top in soup.find_all("div", {"class": "localListAreaEHuyq"}):
            # print(f"top={top}")
            for purchased_date in top.find_all(
                "p", {"class": "purchasedListTitleiBWYR"}
            ):
                # print(f"purchased_date={purchased_date}")
                purchased_date_text = purchased_date.text
                print(f"purchased_date_text={purchased_date_text}")

                parent = purchased_date.parent
                if parent is None:
                    continue
                for div_tag in parent.find_all(
                    "div", {"class": "localListProductzKID2"}
                ):
                    anchor_tag = div_tag.find("a")
                    # print(f"anchor_tag={anchor_tag}")
                    if anchor_tag is None:
                        continue
                    url = anchor_tag.get("href", "")
                    print(f"url={url}")
                    if not isinstance(url, str):
                        continue
                    product_id = Util.extract_base("product_id", url)
                    print(f"product_id={product_id}")
                    if product_id is None:
                        continue
                    span_tag = anchor_tag.find("span", {"class": "defaultClassmE6be"})
                    print(f"span_tag={span_tag}")
                    if span_tag is None:
                        continue
                    kind = span_tag.text
                    print(f"kind={kind}")
                    namex = anchor_tag.find("div", {"class": "productTitleCMVya"})
                    print(f"namex={namex}")
                    if namex is None:
                        continue
                    title = namex.text
                    print(f"title={title}")
                    p_tag = anchor_tag.find("p", {"class": "circleNameGWNom"})
                    print(f"p_tag={p_tag}")
                    if p_tag is None:
                        continue
                    circle_name = p_tag.text
                    print(f"circle_name={circle_name}")
                    work_info = self.WorkInfo(
                        target=target,
                        url=url,
                        product_id=product_id,
                        purchased_date=purchased_date_text,
                        kind=kind,
                        title=title,
                        circle_name=circle_name,
                        sequence=self.sequence,
                    )
                    result = self.add_assoc(work_info)
                    if result:
                        append_count += 1
                    else:
                        no_append_count += 1
        info.append_count = append_count
        info.no_append_count = no_append_count
        self.append_count += append_count
        self.no_append_count += no_append_count
        print(f"append_count={append_count}")
        print(f"no_append_count={no_append_count}")
        print(f"len(self.links_assoc)={len(self.links_assoc)}")
        return self.links_assoc
