from typing import Any, Dict, List
from urllib.parse import parse_qs, urlparse

from bs4.element import Tag
from yklibpy.common.info import Info
from yklibpy.htmlparser.progress import Progress
from yklibpy.htmlparser.scraper import Scraper


class UdemyScraper(Scraper):
    class WorkInfo:
        def __init__(
            self,
            url: str,
            title: str,
            course_id: str,
            instructors: List[str],
            progress: Progress,
            sequence: int,
        ):
            self.sequence = sequence
            # URI形式のチェック
            parsed = urlparse(url)
            if not parsed.scheme:
                raise ValueError(f"url '{url}' is not a valid URI: missing scheme")
            if not parsed.netloc and not parsed.path and not parsed.fragment:
                raise ValueError(
                    f"URL '{url}' is not a valid URI: missing authority, path, or fragment"
                )
            self.url = url
            self.title = title
            self.course_id = course_id
            self.instructors = instructors
            self.progress = progress.to_dict()

        def to_assoc(self):
            assoc = Scraper._to_assoc(self.title, self.url, self.sequence)
            assoc["course_id"] = self.course_id
            assoc["instructors"] = self.instructors
            assoc["progress"] = self.progress
            return assoc

    def __init__(self, sequence: int):
        """Initialize Udemy-specific scraper state.

        Returns:
          None
        """
        super().__init__(sequence)

    def scrape(self, info: Info) -> Dict[str, Dict[str, Any]]:
        """Extract Udemy dashboard cards and convert them into records.

        Args:
          info (Info): Parsed HTML container and counters for the current file.

        Returns:
          Dict[str, Dict[str, Any]]: Dictionary of course records keyed by course_id.
        """
        print("udemyscraper scrape")
        soup = info.soup
        append_count = 0
        no_append_count = 0
        """divの処理"""
        for div_tag in soup.find_all(
            "div", {"class": "enrolled-course-card--container--WJYo9"}
        ):
            # print(f'div_tag={div_tag}')
            a_tag = div_tag.find("a")
            if a_tag is None:
                continue
            href = a_tag.get("href", "#")
            url = href if isinstance(href, str) else "#"
            title = a_tag.get_text(strip=True)
            course_id = self.get_course_id_from_url(url)

            instructors = self.get_instructors(div_tag)
            progress = self.get_progress(div_tag)

            # Extract course_id from URL parameters
            work_info = self.WorkInfo(
                url=url,
                title=title,
                course_id=course_id,
                instructors=instructors,
                progress=progress,
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
        print(
            f"###############   udemyscraper scrape len( self.links_assoc )={len(self.links_assoc)}"
        )
        return self.links_assoc

    def get_instructors(self, div_tag: Tag) -> List[str]:
        """Pull the instructor text from a course card.

        Args:
          div_tag (Tag): Card container.

        Returns:
          List[str]: Instructor names (comma-delimited string kept for backward
          compatibility when not parsed further).
        """
        instructors = ["_0_"]
        child_div = div_tag.find(
            "div",
            {"data-purpose": "safely-set-inner-html:course-card:visible-instructors"},
        )
        if child_div is not None:
            instructor_text = child_div.get_text(strip=True)
            instructors = [instructor_text] if instructor_text else ["_0_"]

        return instructors

    def get_course_id_from_url(self, url: str | None) -> str:
        if isinstance(url, str):
            if url and url != "#":
                try:
                    parsed_url = urlparse(url)
                    query_params = parse_qs(parsed_url.query)
                    course_id = query_params.get("course_id", [""])[0]
                except Exception:
                    course_id = ""
            else:
                course_id = ""
        else:
            course_id = ""

        return course_id

    def get_progress(self, div_tag: Tag) -> Progress:
        """Convert the progress meter DOM node into a :class:`Progress`.

        Args:
            div_tag (Tag): Course card container element.

        Returns:
            Progress: Object encapsulating min/max/current values.
        """
        # meter_div = div_tag.find('div', {'data-purpose': 'meter'})
        meter_div = div_tag.find(
            "div", {"class": "ud-meter meter-module--meter--9-BwT"}
        )

        meter_str = ""
        valuemin = "0"
        valuemax = "100"
        valuenow = "0"
        if meter_div is not None:
            # meter = meter_div.get_text(strip=True)
            aria_label = meter_div.get("aria-label", "")
            meter_str = aria_label if isinstance(aria_label, str) else ""
            aria_valuemin = meter_div.get("aria-valuemin", "0")
            valuemin = aria_valuemin if isinstance(aria_valuemin, str) else "0"
            aria_valuemax = meter_div.get("aria-valuemax", "100")
            valuemax = aria_valuemax if isinstance(aria_valuemax, str) else "100"
            aria_valuenow = meter_div.get("aria-valuenow", "0")
            valuenow = aria_valuenow if isinstance(aria_valuenow, str) else "0"
        else:
            meter_value = f"{valuemin}-{valuemax}-{valuenow}"
            print(f"#### meter2={meter_value}")

        progress = Progress(
            meter_str=meter_str, valuemin=valuemin, valuemax=valuemax, valuenow=valuenow
        )
        return progress

    def add_assoc(
        self,
        work_info: "UdemyScraper.WorkInfo",
    ) -> bool:
        Scraper._add_assoc(
            self.links_assoc,
            work_info.course_id,
            work_info.sequence,
            work_info.to_assoc(),
        )

        return True
