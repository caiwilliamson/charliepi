from peewee import SqliteDatabase, Model, FloatField, DateTimeField
from datetime import datetime

db = SqliteDatabase('charliepi_web.db')

class SensorData(Model):
    temperature = FloatField()
    humidity = FloatField()
    timestamp = DateTimeField(default=datetime.now)

    class Meta:
        database = db

db.connect()
db.create_tables([SensorData])
