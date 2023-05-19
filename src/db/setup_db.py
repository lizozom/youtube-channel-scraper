from peewee import SqliteDatabase
from consts import DB_NAME
from db.models import YouTubeChannel, YouTubeVideo

db = SqliteDatabase(DB_NAME)
db.connect()

# Create the tables.
db.create_tables([YouTubeChannel, YouTubeVideo])

print("Done setting up the database.")
