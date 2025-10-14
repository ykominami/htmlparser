from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import os

def _parse_html_file(file_path: str) -> Optional[BeautifulSoup]:
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
        with open(file_path, 'r', encoding='utf-8') as f:
            # Create a BeautifulSoup object using the lxml parser
            soup = BeautifulSoup(f, 'lxml')
            return soup
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def _extract_links_from_soup(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """
    Extracts all links and their anchor text from a BeautifulSoup object.

    This helper function iterates through all anchor (<a>) tags found in the soup
    and extracts the 'href' attribute and the tag's text content.

    Args:
        soup: The BeautifulSoup object to extract links from.

    Returns:
        A list of dictionaries, where each dictionary represents a link
        with 'url' and 'text' keys.
    """
    links_list = []
    for h3_tag in soup.find_all('h3'):
        data_purpose = h3_tag.get('data-purpose', '#')
        print(f'data_purpose={data_purpose}')
        if data_purpose != 'course-title-url':
            continue

        a_tag = h3_tag.find('a')
        url = a_tag.get('href', '#')
        # Get the visible text of the link, stripping whitespace.
        text = a_tag.get_text(strip=True)
        if url: # Ensure there is a URL
            links_list.append({'url': url, 'text': text})
    return links_list

def get_links_from_html(file_path: str) -> List[Dict[str, str]]:
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
    soup = _parse_html_file(file_path)
    if soup:
        return _extract_links_from_soup(soup)
    return []

def loop(dir_path: str):
    for file in os.listdir(dir_path):
        if file.endswith(".html"):
            extracted_links = get_links_from_html(os.path.join(dir_path, file))
            if extracted_links:
                print(f"Found {len(extracted_links)} links in '{file}':\n")
                for link in extracted_links:
                    print(f"  Text: {link['text']}")
                    print(f"  URL:  {link['url']}\n")
            else:
                print(f"Could not find any links or failed to read the file '{file}'.")

        break

if __name__ == "__main__":
    # main.py
    # from link_extractor import get_links_from_html

    # Define the path to your HTML file
    # html_file = 'example.html'
    # html_file = 'new_event_list.html'
    dir = 'C:/Users/ykomi/Downloads/SAVE_HTML/Udemy'
    loop(dir)
