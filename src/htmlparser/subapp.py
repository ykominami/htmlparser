from yklibpy.htmlparser.app import App
from yklibpy.htmlparser.scraper import Scraper

from htmlparser.amazonsavedcartscraper import AmazonSavedCartScraper
from htmlparser.fanzadoujinbasketscraper import FanzaDoujinBasketScraper
from htmlparser.fanzadoujinpurchasedscraper import FanzaDoujinPurchasedScraper
from htmlparser.kuscraper import KUScraper
from htmlparser.udemyscraper import UdemyScraper


class Subapp(App):
    """
    Appクラスを継承したサブクラス
    """
    def create_scraper(self, mode: str, sequence: int) -> Scraper | None:
        """Build the appropriate scraper implementation for the requested mode.

        Args:
            mode (str): Logical identifier such as ``"udemy"`` or ``"h3"``.

        Returns:
            Scraper: Concrete scraper that knows how to parse the given site, or
            ``None`` when the mode is unsupported.
        """
        print(f"mode={mode}")
        if mode == "udemy":
            return UdemyScraper(sequence)
            # return H3Scraper()
            # return AScraper()
        elif mode == "ku":
            return KUScraper(sequence)
        elif mode == "fanza_doujin_basket":
            return FanzaDoujinBasketScraper(sequence)
        elif mode == "fanza_doujin_purchased":
            return FanzaDoujinPurchasedScraper(sequence)
        elif mode == "amazon_saved_cart":
            # print(f'mode={mode}')
            return AmazonSavedCartScraper(sequence)
        else:
            print(f"mode={mode} is not supported")
            return None
