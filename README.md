# NEWSBOTAI
## About
**NEWSBOTAI** scrapes Reddit for links and summarizes them into tweets with ChatGPT. 
## Dependencies 
• PRAW (Python Reddit API Wrapper) pulls posts from reddit. 

• Newspaper3k reads and summarize article links

• Flask for API

• Electron for WebUI

• NodeJS for WebUI

• Conda for environment management (or any other environment manager, not technically required but recommended and the auto setup will try to use conda)

## Installation

Download the repo `git clone <link>`

Make an enviornment `conda create -n YOURNAMEHERE` and activate it `conda activate YOURNAMEHERE`


If you dont want to use a virtual environment, good luck!

Enter the repo directory `cd newsbot`

Install all the dependencies `pip install -r requirements.txt` ***OR*** `conda install --file requirements.txt`

run `python newsbot_cli.py`

Follow prompts. 

*Optional:* Setup an alias.


## First Time Setup
`python newsbot_cli.py`

Follow the prompts. 

You will need an openai api key and a reddit api key. Your useragent can be anything. Your defualt subreddit can be whatever you want, but I only have tested it on subreddits that exclusively post links like r/worldnews.

API keys and other defaults are saved in the .env file in the root directory. You can edit these after running the script once. Delete the .env file if you want to run the setup again.

## Usage ( CLI )

Command Line Interface Usage:

`python newsbot_cli.py --help`

## Usage ( API )

`python newsbot_cli.py api`

Starts flask server on 127.0.0.1:5000

Not all the commands work yet. Check newsbot_api.py for the full list of commands.

## Future Enhancements
• Twitter integration

• AI generate image based on article

## Why?
I made this for fun.


