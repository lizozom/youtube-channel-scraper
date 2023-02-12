### YouTube Channel Scraper


## Configuration

* Copy .env.tmp and name it `.env`
* Generate a YouTube `YOUTUBE_API_KEY` and paste it into the `.env` file.
* If you want to use caption scraping, install AdBlock locally and paste it's full path into the `.env` file.
* If you want results to be stored in `Elasticsearch`, create an Elastic cloud account and paste it's details into a file named `elastic.ini`
* Create a new virtual environment by running `python -m venv env` and then enable the environment with `source env/bin/activate`
* Install all python dependencies with `pip install -r requirements.txt` 
* Set a list of channel names in `consts.py`

## Fetch channel and video metadata 

To fetch all channel and video data, or fetch fresh videos for existing channels run - 

`python index.py fetch`

You may specify a specific channel - 

`python index.py fetch --channel 'Guga Foods'`

## Fetch video captions

To fetch all video captions, you must specify either a channel name or a video id - 

`python index.py fetch --channel 'Guga Foods'`
`python index.py fetch --video xOzGa4al4Ag`
