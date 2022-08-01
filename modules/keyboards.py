from telepotpro.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from modules.helpers import dateToString


def program_list(pages: list, day: int=0, page: int=0):
    prevDay = datetime.now() + timedelta(days=day-1)
    nextDay = datetime.now() + timedelta(days=day+1)
    keyboard = []

    # Append page navigation only if there is multiple pages
    if len(pages) > 1:
        if page == 0:
            page_line = [InlineKeyboardButton(text=f"Pag. {page+2} ▶️", callback_data=f"list#{day}.{page+1}")]
        elif page == len(pages)-1:
            page_line = [InlineKeyboardButton(text=f"◀️ Pag. {page}", callback_data=f"list#{day}.{page-1}")]
        else:
            page_line = [
                InlineKeyboardButton(text=f"◀️ Pag. {page}", callback_data=f"list#{day}.{page-1}"),
                InlineKeyboardButton(text=f"Pag. {page+2} ▶️", callback_data=f"list#{day}.{page+1}")
            ]
        keyboard.append(page_line)

    if day == 0:
        day_line = [InlineKeyboardButton(text=f"{dateToString(nextDay)} ⏭", callback_data=f"list#{day+1}.0")]
    elif day == 7:
        day_line = [InlineKeyboardButton(text=f"⏮ {dateToString(prevDay)}", callback_data=f"list#{day-1}.0")]
    else:
        day_line = [
            InlineKeyboardButton(text=f"⏮ {dateToString(prevDay)}", callback_data=f"list#{day-1}.0"),
            InlineKeyboardButton(text=f"{dateToString(nextDay)} ⏭", callback_data=f"list#{day+1}.0")
        ]
    keyboard.append(day_line)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
