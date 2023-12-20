from datetime import datetime

from peewee import DateTimeField, FloatField, Model, SqliteDatabase

db = SqliteDatabase("charliepi_web.db")


class Sht30Reading(Model):
    temperature = FloatField()
    humidity = FloatField()
    timestamp = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        indexes = ((("timestamp",), False),)


db.connect()
db.create_tables([Sht30Reading])
