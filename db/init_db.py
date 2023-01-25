from peewee import *
from consts import DB_NAME
from video import YouTubeChannel, YouTubeVideo
 
db = SqliteDatabase(DB_NAME)
db.connect()

# Create the tables.
db.create_tables([YouTubeChannel, YouTubeVideo])
