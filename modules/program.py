from datetime import datetime

class Program:
    genre_emojis = {
            "_default": "📺",
            "Mondo e Tendenze": {
                "_default": "🌍",
                "Documentario": "🎥"
            },
            "Informazione": {
                "_default": "📑",
                "Notiziario": "📰",
                "Sport": "🎱"
            },
            "Film": {
                "_default": "🎬"
            },
            "Intrattenimento": {
                "_default": "🍿"
            },
            "Sport": {
                "_default": "🏀",
                "Motori": "🏎"
            }
        }

    def __init__(self, index: int, id: int, genre: str, subgenre: str, thumbnail: str,
                 duration: int, start_time: str, end_time: str, start_date: datetime,
                 end_date: datetime, title: str, description: str, is_prima: bool):
        self.index = index
        self.id = id
        self.genre = genre
        self.subgenre = subgenre
        self.thumbnail = thumbnail
        self.duration = duration
        self.start_time = start_time
        self.end_time = end_time
        self.start_date = start_date
        self.end_date = end_date
        self.title = title
        self.description = description
        self.is_prima = is_prima

    @classmethod
    def from_dict(cls, data: dict):
        start_date = datetime.strptime(data["dateStart"], "%Y-%m-%d %H:%M")
        end_date = datetime.strptime(data["dateEnd"], "%Y-%m-%d %H:%M")
        is_prima = str(data["prima"]).lower() == "true"
        return cls(int(data["index"]), int(data["id"]), data["genre"], data["subgenre"], data["thumbnail"],
                   int(data["duration"]), data["starttime"], data["endtime"], start_date,
                   end_date, data["title"], data["description"], is_prima)

    @classmethod
    def from_div_list(cls, div_list: list):
        data = {
            div["class"][0]: div.text
            for div in div_list
        }
        return cls.from_dict(data)

    def starts_after(self, limit: datetime) -> bool:
        return self.start_date > limit

    def ends_after(self, limit: datetime) -> bool:
        return self.end_date > limit

    def short_description(self, max_length: int=70) -> str:
        desc = self.description
        if len(desc) > max_length:
            desc = desc[:max_length - 3] + "..."
        return desc

    def get_emoji(self) -> str:
        emoji = self.genre_emojis.get(self.genre, self.genre_emojis["_default"])
        if type(emoji) is dict:
            emoji = emoji.get(self.subgenre, emoji["_default"])
        return emoji

    def prettify(self, with_description: bool=True) -> str:
        pretty = f"{self.get_emoji()} {self.start_time} | <b>{self.title}</b>"
        if with_description:
            pretty += f"\n<i>{self.short_description()}</i>"
        return pretty
