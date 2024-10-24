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

## Usage

**Setup**

Download the repo `git clone <repo>`

Make an enviornment `conda create -n YOURNAMEHERE` and activate it `conda activate YOURNAMEHERE`

Install all the dependencies `pip install -r requirements.txt`

run `python newsbot_cli.py`

Follow prompts to setup a conda environment and install the dependencies

**Running**

Command Line Interface Usage:

`python newsbot_cli.py --help`

Electron WebUI Usage:

• run `python newsbot_cli.py api` to start the flask server

• in a new shell, run `npm start` to start the Electron WebUI

• click the button to start pulling down articles. 

## Future Enhancements
• Post Tweets Directly to Twitter

• Installer script for optimal setup
• AI generate images based on article content

• Fuse summary and generated images into vertical videos with ffmpeg with voiceover

## Why?
Learn about APIs and LLMs, and build something goofy, practice front and backend development.

