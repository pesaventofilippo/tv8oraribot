from datetime import datetime, date

class Program:
    def __init__(self, title: str, start_datetime: datetime, end_datetime: datetime, thumbnail: str):
        self.title = title
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.thumbnail = thumbnail

    @classmethod
    def from_dict(cls, data: dict, context_date: date):
        stttime = data["subtitle"]["text"].split(" - ")[0]
        endtime = data["subtitle"]["text"].split(" - ")[1]
        start_datetime = datetime.combine(context_date, datetime.strptime(stttime, "%H:%M").time())
        end_datetime = datetime.combine(context_date, datetime.strptime(endtime, "%H:%M").time())
        return cls(
            title=data["title"]["text"],
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            thumbnail=data["image"]["src"]
        )

    def starts_after(self, limit: datetime) -> bool:
        return self.start_datetime > limit

    def ends_after(self, limit: datetime) -> bool:
        return self.end_datetime > limit

    @property
    def emoji(self) -> str:
        return "📺"

    @property
    def start_time(self) -> str:
        return self.start_datetime.strftime("%H:%M")

    @property
    def end_time(self) -> str:
        return self.end_datetime.strftime("%H:%M")

    @property
    def pretty_string(self) -> str:
        return f"{self.emoji} {self.start_time} | <b>{self.title}</b>"
