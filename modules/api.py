from requests import get
from datetime import datetime
from bs4 import BeautifulSoup
from modules.Program import Program


class InvalidDayError(Exception):
    def __init__(self):
        self.message = "The day must be between 0 (today) and 7 (days in the future)"


class TV8Api:
    def __init__(self):
        self._cache = {}
        self._last_updated = None

    def _requestProgramsList(self, day: int=0) -> list[Program]:
        # Check if the day is in a valid range
        if day < 0 or day > 7:
            raise InvalidDayError

        # Clear cache if outdated
        if self._last_updated is None or datetime.now().date() != self._last_updated:
            self._cache = {}

        # Check if day is already present in cache
        if self._cache.get(day):
            return self._cache[day]

        # Request new data from website
        page = get(f"https://tv8.it/guidatv/programmi.{day}.html")
        soup = BeautifulSoup(page.text, "lxml")
        data_list = soup.find(id="guidatv_GetProgramList")
        data_list = data_list.find_all("div", {"class": "itemParent"})

        programs = []
        last_stime = ""
        for data in data_list:
            div_list = data.findChildren("div")
            p = Program.from_div_list(div_list)

            # Remove all programs of the next day (the website returns duplicates)
            if p.start_time < last_stime: break
            last_stime = p.start_time

            programs.append(p)

        # Cache retrieved data and return
        self._cache[day] = programs
        self._last_updated = datetime.now().date()
        return programs

    def getProgramList(self, *, day: int=0, end_after: datetime=None, split_pages: int=None) -> list:
        # If end_after is specified, remove programs that end before that
        if end_after:
            result = [p for p in self._requestProgramsList(day) if p.ends_after(end_after)]
        else:
            result = self._requestProgramsList(day)

        # If split_pages is specified, split programs in pages with N programs each
        if split_pages:
            result = [result[x:x+split_pages] for x in range(0, len(result), split_pages)]

        return result
