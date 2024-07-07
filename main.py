from handlers.DBHandler import DBHandler

with DBHandler() as db:
    result = db.select("select * from test")
    print(result)