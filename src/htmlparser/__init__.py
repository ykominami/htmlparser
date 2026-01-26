from htmlparser.top import amain, clearmain, count, print_list_text, prepare
from htmlparser.topconfigdb import TopConfigDb
from htmlparser.subapp import Subapp
from htmlparser.amazonsavedcartscraper import AmazonSavedCartScraper
from htmlparser.fanzadoujinbasketscraper import FanzaDoujinBasketScraper
from htmlparser.fanzadoujinpurchasedscraper import FanzaDoujinPurchasedScraper
from htmlparser.kuscraper import KUScraper
from htmlparser.udemyscraper import UdemyScraper

__all__ = [
    "Subapp",
    "AmazonSavedCartScraper",
    "FanzaDoujinBasketScraper",
    "FanzaDoujinPurchasedScraper",
    "KUScraper",
    "Scraper",
    "UdemyScraper",
    "TopConfigDb",
    "Subapp",
    "AmazonSavedCartScraper",
    "FanzaDoujinBasketScraper",
    "FanzaDoujinPurchasedScraper",
    "KUScraper",
    "Scraper",
    "UdemyScraper",
    "amain",
    "clearmain",
    "count",
    "print_list_text",
    "prepare",
    "TopConfigDb"
]

if __name__ == "__main__":
    amain()

