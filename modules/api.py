import pytz
from requests import get
from datetime import datetime, timedelta
from dateutil import parser as dateparser


class Content:
    _genre_emojis = {
        "_default": "📺",
        "Mondo e Tendenze": {
            "_default": "🌍",
            "Documentario": "🎥"
        },
        "Informazione": {
            "_default": "📑",
            "Notiziario": "🗞",
            "Sport": "🎱"
        },
        "Film": {
            "_default": "🎬",
            "Romantico": "💘",
            "Thriller": "🕷",
            "Drammatico": "😢",
            "Commedia": "😂",
            "Azione": "💥",
            "Fantascienza": "🚀"
        },
        "Intrattenimento": {
            "_default": "🍿",
            "Show": "🍿",
            "Reality Show": "🎥",
            "Fiction": "📚"
        },
        "Sport": {
            "_default": "⚽️",
            "Motori": "🏎"
        }
    }

    def __init__(self, uuid: str, title: str, episode: int, season: int,
                 genre: str, subgenre: str, cover: str):
        self.uuid = uuid
        self.title = title
        self.episode = episode
        self.season = season
        self.genre = genre
        self.subgenre = subgenre
        self.cover = cover

    @property
    def emoji(self) -> str:
        res = self._genre_emojis.get(self.genre, self._genre_emojis["_default"])
        if type(res) is dict:
            res = res.get(self.subgenre, res["_default"])
        return res


class Program:
    def __init__(self, _id: int, title: str, desc_title: str, description: str,
                 start_datetime: datetime, end_datetime: datetime,
                 content: Content):
        self._id = _id
        self.title = title
        self.desc_title = desc_title
        self.description = description
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.content = content

    @classmethod
    def from_dict(cls, data: dict):
        def get_cover_url(images_map: list) -> str:
            for element in images_map:
                if element["key"] == "cover":
                    return "https://guidatv.sky.it" + element["img"]["url"]
            return None

        def convert_datestring(date_string: str) -> datetime:
            date = dateparser.parse(date_string) # Convert date string
            date = date.astimezone(pytz.timezone("Europe/Rome")) # Convert to local timezone
            date = date.replace(tzinfo=None) # Remove timezone info
            return date

        return cls(
            _id=data["eventId"],
            title=data["eventTitle"],
            desc_title=data["epgEventTitle"],
            description=data["eventSynopsis"],
            start_datetime=convert_datestring(data["starttime"]),
            end_datetime=convert_datestring(data["endtime"]),
            content=Content(
                uuid=data["content"]["uuid"],
                title=data["content"]["contentTitle"],
                episode=data["content"].get("episodeNumber", None),
                season=data["content"].get("seasonNumber", None),
                genre=data["content"]["genre"]["name"],
                subgenre=data["content"]["subgenre"]["name"],
                cover=get_cover_url(data["content"]["imagesMap"])
            )
        )

    def starts_after(self, limit: datetime) -> bool:
        return self.start_datetime > limit

    def ends_after(self, limit: datetime) -> bool:
        return self.end_datetime > limit

    @property
    def start_time(self) -> str:
        return self.start_datetime.strftime("%H:%M")

    @property
    def end_time(self) -> str:
        return self.end_datetime.strftime("%H:%M")

    @property
    def emoji(self) -> str:
        return self.content.emoji

    def short_description(self, max_length: int=85) -> str:
        desc = self.description
        if len(desc) > max_length:
            desc = desc[:max_length - 3] + "..."
        return desc

    def prettify(self, with_description: bool=True) -> str:
        pretty = f"{self.emoji} {self.start_time} | <b>{self.title}</b>"
        if with_description:
            pretty += f"\n<i>{self.short_description()}</i>"
        return pretty


class TV8Api:
    def __init__(self):
        self._cache = {}
        self._last_updated = None

    def _requestProgramsList(self, day: int=0) -> list[Program]:
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

        if not data.get("events"):
            return []

        programs = []
        last_stime = ""
        for prog_info in data["events"]:
            p = Program.from_dict(data=prog_info)

            # Remove all programs of the next day (the website returns duplicates)
            if p.start_time < last_stime: break
            last_stime = p.start_time

            programs.append(p)

        # Cache retrieved data and return
        self._cache[day] = programs
        self._last_updated = now_date
        return programs

    def getProgramList(self, *, day: int=0, end_after: datetime=None, split_pages: int=None) -> list[Program] | list[list[Program]]:
        result = self._requestProgramsList(day)

        # If end_after is specified, remove programs that end before that
        if end_after:
            result = [p for p in result if p.ends_after(end_after)]

        # If split_pages is specified, split programs in pages with <split_pages> programs each
        if split_pages:
            result = [result[i:i + split_pages] for i in range(0, len(result), split_pages)]

        return result
