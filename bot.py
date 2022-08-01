from time import sleep
from telepotpro import Bot
from json import load as jsload
from pony.orm import db_session, select
from datetime import datetime, timedelta
from os.path import abspath, dirname, join
from telepotpro.exception import TelegramError, BotWasBlockedError

from modules.api import TV8Api
from modules.database import User
from modules import keyboards, helpers

with open(join(dirname(abspath(__file__)), "settings.json")) as settings_file:
    js_settings = jsload(settings_file)

bot = Bot(js_settings["token"])
api = TV8Api()


def createProgramsList(day: int=0, page: int=0):
    plist = api.getProgramList(day=day, end_after=datetime.now(), split_pages=6)
    programs = [p.prettify() for p in plist[page]]
    date = datetime.now() + timedelta(days=day)

    text = f"📺 <b>LISTA PROGRAMMI DI {helpers.dateToString(date).upper()}</b>\n" \
           f"Pagina {page+1}/{len(plist)}\n\n"
    text += "\n\n".join(programs)
    keyboard = keyboards.program_list(plist, day, page)
    return text, keyboard


@db_session
def reply(msg):
    chatId = msg["chat"]["id"]
    text = msg.get("text", "")
    user = User.get(chatId=chatId) if User.exists(lambda u: u.chatId == chatId) else User(chatId=chatId)

    if text == "/start":
        bot.sendMessage(chatId, f"Ciao, <b>{msg['from']['first_name']}</b>! 👋\n\n"
                                "Ecco cosa puoi fare con questo bot:\n"
                                "/oggi: la lista di programmi in onda oggi\n"
                                "/adesso: il programma attualmente in onda\n"
                                "/lista: lista dettagliata dei prossimi programmi\n\n"
                                "Premi /help per avere più informazioni!", parse_mode="HTML")

    elif text == "/oggi":
        programs = [p.prettify() for p in api.getProgramList(end_after=datetime.now())]
        bot.sendMessage(chatId, "📺 <b>LISTA PROGRAMMI DI OGGI</b>\n\n" + "\n\n".join(programs), parse_mode="HTML")

    elif text == "/adesso":
        now = api.getProgramList(end_after=datetime.now())[0]
        bot.sendMessage(chatId, f"<a href='{now.thumbnail}'>{now.get_emoji()}</a> In onda: <b>{now.title}</b>\n"
                                f"({now.start_time} - {now.end_time})\n\n"
                                f"<i>{now.description}</i>", parse_mode="HTML")

    elif text == "/lista":
        text, keyboard = createProgramsList()
        bot.sendMessage(chatId, text, parse_mode="HTML", reply_markup=keyboard)

    elif text == "/about":
        bot.sendMessage(chatId, "ℹ️ <b>Informazioni sul bot</b>\n"
                                "Visualizza rapidamente la programmazione e gli orari di TV8, il programma "
                                "attualmente in onda e molto altro, tutto da Telegram con una comoda interfaccia!\n\n"
                                "<b>Sviluppo:</b> Filippo Pesavento\n"
                                "<b>Hosting:</b> Filippo Pesavento\n\n"
                                "<a href=\"https://t.me/pesaventofilippo\">Contattami</a>",
                        parse_mode="HTML", disable_web_page_preview=True)

    elif text == "/help":
        bot.sendMessage(chatId, "Ciao, sono <b>TV8 Orari Bot</b>! 👋🏻\n"
                                "Posso aiutarti a visualizzare i programmi di TV8, e quando andranno in onda.\n\n"
                                "<b>Lista dei comandi</b>:\n"
                                "- /start - Avvia il bot\n"
                                "- /oggi - Vedi la lista dei programmi in onda oggi\n"
                                "- /adesso - Descrizione dettagliata del programma attualmente in onda\n"
                                "- /lista - Vedi la lista dei prossimi programmi\n"
                                "- /about - Informazioni sul bot\n"
                                "- /help - Visualizza questo messaggio"
                                "", parse_mode="HTML")

    elif text.startswith("/broadcast ") and helpers.isAdmin(chatId):
        text = text.split(" ", 1)[1]
        pendingUsers = select(u.chatId for u in User)[:]
        userCount = len(pendingUsers)
        for u in pendingUsers:
            try:
                bot.sendMessage(u, text, parse_mode="HTML", disable_web_page_preview=True)
            except (TelegramError, BotWasBlockedError):
                userCount -= 1
        bot.sendMessage(chatId, f"📢 Messaggio inviato a {userCount} utenti!")

    elif text == "/users" and helpers.isAdmin(chatId):
        userCount = len(select(u for u in User)[:])
        bot.sendMessage(chatId, f"👤 Utenti: <b>{userCount}</b>", parse_mode="HTML")

    # Text is not a keyword
    else:
        bot.sendMessage(chatId, "Non ho capito...\n"
                                "Serve aiuto? Premi /help")


def button(msg):
    chatId = msg['message']['chat']['id']
    msgId = msg['message']['message_id']
    text = msg['data']
    msgIdent = (chatId, msgId)

    if text.startswith("list"):
        day, page = [int(x) for x in text.split("#")[1].split(".")]
        text, keyboard = createProgramsList(day, page)
        bot.editMessageText(msgIdent, text, parse_mode="HTML", reply_markup=keyboard)


bot.message_loop({'chat': reply, 'callback_query': button})
while True:
    sleep(60)
