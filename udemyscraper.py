from scraper import Scraper
from info import Info
from urllib.parse import urlparse, parse_qs
from progress import Progress
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from pathlib import Path

class UdemyScraper(Scraper):
  def __init__(self):
    """Initialize Udemy-specific scraper state.

    Returns:
      None
    """
    super().__init__()

  def _extract_links_assoc_from_info(self,info: Info) -> List[Dict[str, str]]:
    """Populate the associative map keyed by course ID.

    Args:
      info (Info): Parsed HTML payload for a file.

    Returns:
      dict: ``links_assoc`` containing course records.
    """
    super()._extract_links_from_info(info)
    self.scrape(info)
    # links_list = self.process_for_udemy(info)
    return self.links_assoc

  def scrape(self, info: Info) -> List[Dict[str, str]]:
    """Extract Udemy dashboard cards and convert them into records.

    Args:
      info (Info): Parsed HTML container and counters for the current file.

    Returns:
      List[Dict[str, str]]: List of record dictionaries appended this run.
    """
    print('udemyscraper scrape')
    soup = info.soup
    append_count = 0
    no_append_count = 0
    """divの処理"""
    for div_tag in soup.find_all('div', {'class': 'enrolled-course-card--container--WJYo9'}):
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
    print(f'###############   udemyscraper scrape len( self.links_list )={ len(self.links_list) }')
    print(f'###############   udemyscraper scrape len( self.links_assoc )={ len(self.links_assoc) }')
    return self.links_list
    
  def get_instructors(self, div_tag) -> List[str]:
    """Pull the instructor text from a course card.

    Args:
      div_tag (BeautifulSoup): Card container.

    Returns:
      List[str]: Instructor names (comma-delimited string kept for backward
      compatibility when not parsed further).
    """
    instructors = ['_0_']
    child_div = div_tag.find('div', {'data-purpose': 'safely-set-inner-html:course-card:visible-instructors'})
    if child_div is not None:
        instructors = child_div.get_text(strip=True)

    return instructors

  def get_course_id_from_url(self, url: str) -> str:
    """Extract ``course_id`` query parameter from a Udemy URL.

    Args:
      url (str): Anchor ``href`` attribute.

    Returns:
      str: Course identifier or empty string when absent.
    """
    if url and url != '#':
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            course_id = query_params.get('course_id', [''])[0]
        except Exception:
            course_id = ''

    return course_id

  def get_progress(self, div_tag: BeautifulSoup) -> Progress:
      """Convert the progress meter DOM node into a :class:`Progress`.

      Args:
          div_tag (BeautifulSoup): Course card container element.

      Returns:
          Progress: Object encapsulating min/max/current values.
      """
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

  def add_list_and_assoc(self, url: str, text: str, course_id: str, instructors: List[str], progress: Progress) -> bool:
      """Insert a new record if the ``course_id`` has not been seen.

      Args:
          url (str): Course URL.
          text (str): Anchor text/label.
          course_id (str): Unique identifier.
          instructors (List[str]): Instructor names.
          progress (Progress): Progress state per card.

      Returns:
          bool: ``True`` when the record was added, else ``False``.
      """
      result = False
      if not course_id in self.links_assoc.keys():
          # instructors = instructors.split(',')
          # print(f'#### add_list_and_assoc instructors={instructors}')
          record = self.make_record(url=url, text=text, course_id=course_id, instructors=instructors, progress=progress)
          # record = self.make_record(url, text, course_id)
          # print(f'=1 record1={record}')

          self.links_assoc[course_id] = record
          # print(f'#### add_list_and_assoc len( self.links_assoc )={ len(self.links_assoc) }')
          self.links_list.append(record)
          result = True
      else:
          pass

      return result

  def make_record(self, url: str, text: str, course_id: str, instructors: List[str], progress: Progress | Dict) -> Dict[str, str]:
      """Construct the normalized record stored in outputs.

      Args:
          url (str): Course URL, must be valid.
          text (str): Display name.
          course_id (str): Identifier used as key.
          instructors (List[str]): Instructor strings.
          progress (Progress | Dict): Progress object or dict.

      Returns:
          Dict[str, str]: Record containing URL/Text/Course_ID/Instructors/Progress.

      Raises:
          ValueError: If the supplied URL lacks a scheme or structure.
      """
      if isinstance(progress, dict):
          progress_dict = progress
      else:
          progress_dict = progress.to_dict()
      # print(f'############ make_record instructors={instructors}')
      # print(f'############ make_record progress_yml={progress_dict}')
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


  def get_link_array(self, extracted_links: List[Dict[str, str]]) -> List[Dict[str, str]]:
      """Convert associative link data into a list of records.

      Args:
          extracted_links (List[Dict[str, str]]): Existing course data.

      Returns:
          List[Dict[str, str]]: Cloned records via :meth:`make_record`.
      """
      print(f'###############   get_link_array len(extracted_links)={len(extracted_links)}')
      return [self.make_record(url=link['URL'], text=link['Text'], course_id=link['Course_ID'], instructors=link['Instructors'], progress=link['Progress']) for link in extracted_links]

