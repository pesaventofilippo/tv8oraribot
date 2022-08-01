from pony.orm import Database, Required, PrimaryKey

db = Database("sqlite", "../tv8oraribot.db", create_db=True)


class User(db.Entity):
    chatId = PrimaryKey(int, sql_type='BIGINT', size=64)
    status = Required(str, default="normal")


db.generate_mapping(create_tables=True)
