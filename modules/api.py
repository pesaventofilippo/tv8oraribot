from requests import get
from datetime import datetime, timedelta
from modules.program import Program


class TV8Api:
    def __init__(self):
        self._cache = {}
        self._last_updated = None

    def _requestProgramsList(self, day: int=0) -> list:
        # Clear cache if outdated
        now_date = datetime.now().date()
        if self._last_updated is None or now_date != self._last_updated:
            self._cache = {}

        # Check if day is already present in cache
        if self._cache.get(day):
            return self._cache[day]

        # Request new data from website
        target = now_date + timedelta(days=day)
        page = get(f"https://www.tv8.it/api/programming"
                   f"?from={target.isoformat()}T00:00:00Z"
                   f"&to={target.isoformat()}T23:59:59Z")
        data = page.json()

        programs = []
        last_stime = ""
        for prog_info in data:
            p = Program.from_dict(data=prog_info, context_date=target)

            # Remove all programs of the next day (the website returns duplicates)
            if p.start_time < last_stime: break
            last_stime = p.start_time

            programs.append(p)

        # Cache retrieved data and return
        self._cache[day] = programs
        self._last_updated = now_date
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
