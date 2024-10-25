
#
#   newsbotai main script
#   author: @chocolatechimps
#   date: 2024-10-20
#

#
#   import required libraries
#

import os#   os for shell commands
from dotenv import load_dotenv#   environment variable load
import praw#    reddit API requests
import sys# parse positional arguments
from newspaper import Article as Article3k# newspaper3k article parsing
import requests#   import requests to send post request to openai
import json #   for logfile
import time#   for date stamping in logfile
from collections import namedtuple#   for article object
from typing import List, Generator#   for type hinting
from datetime import datetime#   for date stamping 

#
#       Article Object
#

Article = namedtuple('Article', ['title', 'url', 'summary', 'keywords', 'date', 'file_id'])

class ArticleManager:
    #   manipulate Article objects
    def __init__(self):
        self.articles: List[Article] = []
        self.logfile_path = 'content/past_articles.json'
    def truncate_title(self, title: str) -> str:
        #   shortens title to 3 words and adds ellipsis
        #   used for logging
        title = str(title)#   make sure its a string. title could be None
        return " ".join(title.split()[:5]) + "..."
    def add(self, article: Article):#   store article in memory
        self.articles.append(article)#   add article to a list 
    def novel(self, article: Article) -> bool:
        #   make sure article is not a duplicate
        print(f'{bcolors.BLUE}Checking novelty{bcolors.ENDC}')
        with open(self.logfile_path, 'r') as logfile:
            saved_articles = json.load(logfile)
            existing_links = {saved_articles["ARTICLE_LINK"] for saved_articles in saved_articles}  # Load Saved Links
            if article.url in existing_links:
                print(f'{bcolors.RED}Article Is Not Novel: {bcolors.ENDC}{bcolors.ITALICS}{self.truncate_title(article.title)}{bcolors.ENDC}')
                return False
            else:
                print(f'{bcolors.RED}Article Is Novel: {bcolors.ENDC}{bcolors.ITALICS}{self.truncate_title(article.title)}{bcolors.ENDC}')
                return True
    def summarize(self, url) -> str:#   summarize article
        #   use openai to summarize article
        #   use newspaper3k to read the article
        #   download and parse article with newspaper3k
        article_contents = Article3k(url)
        article_contents.download()
        article_contents.parse()

        #   send article to openai for summarization
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": os.getenv("DEFAULT_SUMMARIZATION_CONTEXT")},
                {"role": "user", "content": os.getenv("DEFAULT_SUMMARIZATION_INSTRUCTIONS") + article_contents.text}
            ]
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            print(f'{bcolors.YELLOW}Article Summarized{bcolors.ENDC}')
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            print(f'{bcolors.RED}Error: {response.status_code} - {response.text}{bcolors.ENDC}')
    def set_file_id(self) -> int:
        #   set the file_id of the article
        with open(self.logfile_path, 'r') as logfile:
            saved_articles = json.load(logfile)
            return len(saved_articles) + 1
    def generate_image(self, article: Article = None, url: str = None, summary: str = None):
        # DALLE API call to generate an image for the article
        print(f'{bcolors.ITALICS}Generating Image...{bcolors.ENDC}')
        # parse the input
        if article:
            # this one is easy. if it got an article object, use it
            print(f'{bcolors.BLUE}Using provided article object{bcolors.ENDC}')
        elif article is None:
            #   make an article object if none is provided 
            print(f'{bcolors.RED}No Article Object Provided{bcolors.ENDC}')
            if summary and url:
                #
                #    if it gets both, just use the url
                #
                with open(self.logfile_path, 'r') as logfile:
                    saved_articles = json.load(logfile)
                    existing_links = {saved_articles["ARTICLE_LINK"] for saved_articles in saved_articles}
                    #   if the URL is saved already use that data
                    if url in existing_links:
                        print(f'{bcolors.BLUE}Found Saved Link:{bcolors.ENDC} {url}')
                        for saved_article in saved_articles:
                            if saved_article.get("ARTICLE_LINK") == url:
                                article = Article(
                                    title=saved_article["ARTICLE_TITLE"],
                                    url=saved_article["ARTICLE_LINK"],
                                    summary=saved_article.get("ARTICLE_SUMMARY"),
                                    keywords=saved_article.get("ARTICLE_KEYWORDS", None),
                                    date=saved_article.get("DATE", None),
                                    file_id=saved_article.get("FILE_ID", None)
                                )
                                print(f'{bcolors.BLUE}Found Article:{bcolors.ENDC} {ArticleManager().truncate_title(article.title)}')
                    else:
                        #   if the URL is not saved already, fetch the article from the url
                        article = fetch_article_from_url(url=url)
            elif summary and not url:
                #   if only a summary, make an article object with just the summary and file_id
                #   basically just exists for testing
                print(f'{bcolors.RED}No url provided{bcolors.ENDC}')
                article = Article(title=None, url=None, summary=summary, keywords=None, date=None, file_id=self.set_file_id())
            elif not summary and url:
                #   if only a url, fetch the article from the url
                print(f'{bcolors.RED}No summary provided{bcolors.ENDC}')
                # make a temp article for novelty check
                article = Article(title=None, url=url, summary=None, keywords=None, date=None, file_id=None)
                if self.novel(article):
                    article = fetch_article_from_url(url=url)
                    # if its novel, run a fetch
                else:
                    # if its not novel, use the saved data
                    with open(self.logfile_path, 'r') as logfile:
                        saved_articles = json.load(logfile)
                        existing_links = {saved_articles["ARTICLE_LINK"] for saved_articles in saved_articles}
                        #   if the URL is saved already use that data
                        if url in existing_links:
                            print(f'{bcolors.BLUE}Found Saved Link:{bcolors.ENDC} {url}')
                            for saved_article in saved_articles:
                                if saved_article.get("ARTICLE_LINK") == url:
                                    article = Article(
                                        title=saved_article["ARTICLE_TITLE"],
                                        url=saved_article["ARTICLE_LINK"],
                                        summary=saved_article.get("ARTICLE_SUMMARY"),
                                        keywords=saved_article.get("ARTICLE_KEYWORDS", None),
                                        date=saved_article.get("DATE", None),
                                        file_id=saved_article.get("FILE_ID", None)
                                    )
                                    print(f'{bcolors.BLUE}Found Article:{bcolors.ENDC} {ArticleManager().truncate_title(article.title)}') 
            else:
                #   if nothing is provided, just exit
                print(f'{bcolors.RED}{bcolors.BOLD}SOMETHING WENT WRONG{bcolors.ENDC}')
                exit()
        #   make sure the images directory exists
        SetupManager().image_directory_setup()
        #
        #   TODO : check if theres already an image made for it
        #
        #   make the DALLE API call
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "dall-e-3",
            "prompt": article.summary,
            "n": 1,
            "size": "1024x1024"
        }
        response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=data)
        attempts = 1
        while attempts < 6:
            print(f'{bcolors.BLUE}{attempts} Images Requested{bcolors.ENDC}')
            attempts += 1
            try:
                if response.status_code == 200:
                    print(f'{bcolors.YELLOW}Image Generated{bcolors.ENDC}')
                    image_url = response.json()['data'][0]['url']
                    image_data = requests.get(image_url).content
                    filename = str(article.file_id) + "_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
                    filepath = os.path.join('content/images', filename)
                    with open(filepath, 'wb') as f:
                        f.write(image_data)
                    print(f"{bcolors.YELLOW}Saved As: {bcolors.ENDC}{filepath}")
                    return filepath
                elif response.status_code == 429:
                    print(f'{bcolors.RED}{bcolors.UNDERLINE}Rate Limit Reached{bcolors.ENDC}')
                    print(f'{bcolors.RED}Error: {response.status_code} - {response.text}{bcolors.ENDC}')
                    time.sleep(10)
                elif response.status_code == 400:
                    print(f'{bcolors.RED}{bcolors.UNDERLINE}Content Policy Violation{bcolors.ENDC}')
                    print(f'{bcolors.RED}Error: {response.status_code} - {response.text}{bcolors.ENDC}')
                    time.sleep(1000)# wait until trying again, becuase the filter sometimes doesnt get it right
                    continue
                else:
                    print(f'{bcolors.RED}{bcolors.UNDERLINE}Problem with the DALLE API call{bcolors.ENDC}')
                    print(f'{bcolors.RED}Error: {response.status_code} - {response.text}{bcolors.ENDC}')
            except Exception as e:
                print(f'{bcolors.RED}Error: {e}{bcolors.ENDC}')
                attempts = 5

    def save(self, article: Article, force: bool = False):
        #   save article to json | force = True to save even if not novel
        if not force and not self.novel(article):
            # novelty check so that only novel articles are saved
            print(f'{bcolors.RED}{bcolors.BOLD}Article Not Saved{bcolors.ENDC}')
            return False
        print(f'{bcolors.HIGHLIGHT}Saving Article:{bcolors.ENDC}{bcolors.ITALICS} {self.truncate_title(article.title)}{bcolors.ENDC}')
        
        #   summary assignment
        if hasattr(article, 'summary') and article.summary is not None:
            #   if article already has a summary, skip the assignment
            print(f'Article has a Summary: \n{bcolors.BLUE}{article.summary}{bcolors.ENDC}')
        else:
            print(f'{bcolors.ITALICS}Summary set to None{bcolors.ENDC}')
            pass
        
        #   keywords assignment
        if hasattr(article, 'keywords') and article.keywords is not None:
            #   if article already has keywords, skip the assignment
            print(f'Article Has Keywords: {bcolors.BLUE}{article.keywords}{bcolors.ENDC}')
        else:
            print(f'{bcolors.ITALICS}Setting Keywords:{bcolors.ENDC}{bcolors.BLUE} None{bcolors.ENDC}')

        #   date assignment
        if hasattr(article, 'date') and article.date is not None:
            #   if article already has a date, skip the assignment
            print(f'Article already has a date assigned: {bcolors.BLUE}{article.date}{bcolors.ENDC}')
        else:
            #   if article does not have a date, assign one
            article = article._replace(date=int(time.time()))

        #   file_id assignment
        if hasattr(article, 'file_id') and article.file_id is not None:
            #   if article already has a file_id, skip the assignment
            print(f'{bcolors.BLUE}Article has a file_id assigned: {article.file_id}{bcolors.ENDC}')
        else:
            #   if article does not have a file_id, assign one
            with open(self.logfile_path, 'r') as logfile:
                saved_articles = json.load(logfile)
                article_id = len(saved_articles) + 1
                article = article._replace(file_id=article_id)
        

        #   save article data to logfile
        article_data = {
            "ARTICLE_TITLE": article.title,
            "ARTICLE_LINK": article.url,
            "ARTICLE_SUMMARY": article.summary,
            "ARTICLE_KEYWORDS": article.keywords,
            "DATE": article.date,
            "FILE_ID": str(article.file_id),
        }
        print(f'{bcolors.ITALICS}Saving...{bcolors.ENDC}')
        with open(self.logfile_path, 'r') as logfile:
            saved_articles = json.load(logfile)
            saved_articles.append(article_data)
        with open(self.logfile_path, 'w') as logfile:
            json.dump(saved_articles, logfile, indent=4)
            print(f'{bcolors.YELLOW}Saved \n{bcolors.ENDC}FILE_ID: {bcolors.BLUE}{article.file_id}{bcolors.ENDC}')

#
#       interact with the article manager
#
#       these should probably be in a class
#

def fetch_article_from_reddit(subreddit: str = None, category: str = None, limit: int = 1) -> Generator[Article, None, None]:
    #   general purpose function for fetching articles from a subreddit
    print(f'{bcolors.ITALICS}{bcolors.PINK}Fetching Articles from Reddit...{bcolors.ENDC}')
    #   set the defaults if none are provided
    if subreddit is None:
        subreddit = os.getenv("DEFAULT_SUBREDDIT")
    if category is None:
        category = os.getenv("DEFAULT_SUBREDDIT_CATEGORY")
    if limit is None:
        limit = os.getenv("DEFAULT_LIMIT")
    
    #   print search criteria
    print(f'Subreddit: {bcolors.BLUE}{subreddit}{bcolors.ENDC}')
    print(f'Category: {bcolors.BLUE}{category}{bcolors.ENDC}')
    print(f'Limit: {bcolors.BLUE}{limit}{bcolors.ENDC}')
    
    #   setup praw instance
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_API_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_API_SECRET"),
        user_agent=os.getenv("REDDIT_API_USER_AGENT"),
    )
    #   make API call
    for submission in getattr(reddit.subreddit(subreddit), category)(limit=limit):
        yield Article(submission.title, submission.url, None, None, None, None)

def fetch_article_from_url(url: str) -> Article:
    #   fetch article from url
    #   populates everything except for keywords
    article_data = Article3k(url)
    article_data.download()
    article_data.parse()
    print(f'{bcolors.ITALICS}{article_data.title}{bcolors.ENDC}')
    print(f'{bcolors.BLUE}{url}{bcolors.ENDC}')
    print(f'{ArticleManager().summarize(url)}')
    article = Article(article_data.title, url, ArticleManager().summarize(url), None, int(time.time()), ArticleManager().set_file_id())
    ArticleManager().save(article)
    return article


def harvest(subreddit: str = None, category: str = None, limit: int = 1):
    #    gets articles and does the following:
    #   -   checks if article is novel
    #   -   summarizes article
    #   -   saves article
    print(f'{bcolors.BLUE}Harvesting Articles...{bcolors.ENDC}')
    search_count = 1
    while True:
        for article in fetch_article_from_reddit(subreddit=subreddit, category=category, limit=search_count):
            print(f'Searches: {search_count}')
            if not ArticleManager().novel(article):
                search_count += 1
                pass
            else:
                gpt_summary = ArticleManager().summarize(article.url)
                article = article._replace(summary=gpt_summary)
                ArticleManager().save(article)
                return False

def recall_article(random: bool = False) -> Article:
    """
    Recalls an article from the JSON logfile.
    By default, returns the most recent article.
    If random=True, returns a random article.
    Returns an Article object with fields populated from the JSON data.
    """
    print(f'{bcolors.BLUE}Recalling article{"" if not random else " (random)"}...{bcolors.ENDC}')
    logfile_path = 'content/past_articles.json'
    
    try:
        with open(logfile_path, 'r') as logfile:
            saved_articles = json.load(logfile)
        
        if not saved_articles:
            print(f'{bcolors.RED}No articles found in logfile{bcolors.ENDC}')
            return None
        
        if random:
            import random as rand
            article_data = rand.choice(saved_articles)
        else:
            article_data = max(saved_articles, key=lambda x: x.get('DATE', 0))
        
        return Article(
            title=article_data.get('ARTICLE_TITLE'),
            url=article_data.get('ARTICLE_LINK'),
            summary=article_data.get('ARTICLE_SUMMARY'),
            keywords=article_data.get('ARTICLE_KEYWORDS'),
            date=article_data.get('DATE'),
            file_id=article_data.get('FILE_ID')
        )
    except FileNotFoundError:
        print(f'{bcolors.RED}Logfile not found: {logfile_path}{bcolors.ENDC}')
        return None
    except json.JSONDecodeError:
        print(f'{bcolors.RED}Error decoding JSON from logfile{bcolors.ENDC}')
        return None

def recall_all_articles() -> List[Article]:
    logfile_path = 'content/past_articles.json'
    try:
        with open(logfile_path, 'r') as logfile:
            saved_articles = json.load(logfile)
        
        # Sort articles by date in descending order
        sorted_articles = sorted(saved_articles, key=lambda x: x.get('DATE', 0), reverse=True)
        
        return [
            Article(
                title=article.get('ARTICLE_TITLE'),
                url=article.get('ARTICLE_LINK'),
                summary=article.get('ARTICLE_SUMMARY'),
                keywords=article.get('ARTICLE_KEYWORDS'),
                date=article.get('DATE'),
                file_id=article.get('FILE_ID')
            ) for article in sorted_articles
        ]
    except FileNotFoundError:
        print(f'{bcolors.RED}Logfile not found: {logfile_path}{bcolors.ENDC}')
        return []
    except json.JSONDecodeError:
        print(f'{bcolors.RED}Error decoding JSON from logfile{bcolors.ENDC}')
        return []
def view_article_summary(article: Article):
    if article.summary is None:
        article = ArticleManager().summarize(article)
    print(f'{bcolors.YELLOW}{bcolors.UNDERLINE}Recalled Article:{bcolors.ENDC}{bcolors.ITALICS} {ArticleManager().truncate_title(article.title)}{bcolors.ENDC}')
    print(f'{bcolors.BLUE}Summary: \n{bcolors.ENDC}{bcolors.YELLOW}{article.summary}{bcolors.ENDC}')

# might not be the best way to do this
# the first time setup script is a new file but im not sure if chaning this will break anything yet
class SetupManager:
    def __init__(self):
        pass
    def first_time_setup(self):
        #   backup env file just in case, then delete .env
        if self.dotenv_exists():
            self.backup_env_file(delete_original=True)
        else:
            pass
        # create the conda environment
        if input(f'{bcolors.BLUE}Create Conda Environment? [Y/n]: {bcolors.ENDC}').strip().lower() == 'y':
            environment_name = input(f'{bcolors.BLUE}Name the Conda Environment: {bcolors.ENDC}')
            os.system(f'conda env create -f environment.yml')
            os.system(f'conda activate {environment_name}')
            os.system('pip install -r requirements.txt')
        else:
            pass
        #   setup the .env file
        self.setup_dot_env()

    def backup_env_file(self, delete_original: bool = False):
        #   backup the .env file if one exists, just in case
        backup_file_name = f'.env_backup_{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}'
        try:
            #   not the way i would have done this but if it works it works
            with open('.env', 'r') as original_file:
                with open(backup_file_name, 'w') as backup_file:
                    backup_file.write(original_file.read())
            print(f'{bcolors.YELLOW}Backup of .env created as {backup_file_name}{bcolors.ENDC}')
            
            # Delete the original .env file
            if delete_original:
                os.remove('.env')
                print(f'{bcolors.YELLOW}.env file deleted successfully.{bcolors.ENDC}')
            else:
                print(f'{bcolors.YELLOW}.env file backed up successfully.{bcolors.ENDC}')
        except FileNotFoundError:
            print(f'{bcolors.RED}.env file not found. Backup failed.{bcolors.ENDC}')

    def dotenv_exists(self) -> bool:#   check if .env file exists
        return os.path.exists('.env')
    def dotenv_load(self):
        if self.dotenv_exists():
            load_dotenv()
        else:
            print(f'{bcolors.RED}No .env File Detected. Exiting...{bcolors.ENDC}')
            exit()
    def setup_dot_env(self):#   .env file setup
        print(f'\n\n\n{bcolors.PINK}{bcolors.UNDERLINE}  ~~~  Environment Variables Setup Wizard  ~~~  {bcolors.ENDC}\n\n\n')
        if not self.dotenv_exists():
            print(f'{bcolors.ITALICS}No .env File Detected...{bcolors.ENDC}')
            print(f'{bcolors.ITALICS}{bcolors.PINK}Entering First Time Setup...{bcolors.ENDC}')
            api_key = input(f'{bcolors.BLUE}Enter OPENAI API KEY: {bcolors.ENDC}')
            reddit_api_client_id = input(f'{bcolors.BLUE}Enter Reddit API Client ID: {bcolors.ENDC}')
            reddit_api_secret = input(f'{bcolors.BLUE}Enter Reddit API Secret: {bcolors.ENDC}')
            reddit_api_user_agent = input(f'{bcolors.BLUE}Enter Reddit API User Agent: {bcolors.ENDC}')
            # prob want to do the reddit setup on its own
            default_subreddit_to_scrape = input(f'{bcolors.BLUE}Enter Default Subreddit to Scrape: {bcolors.ENDC}')
            default_subreddit_category = input(f'{bcolors.BLUE}Enter Category to Browse [top, hot, new, rising]: {bcolors.ENDC}')
            default_summarization_context = "You are a twitter journalist that summarizes articles and realys them to adoring fans. Have a dry sense of humor. Focus on being clear in communication. Keep all responses under 480 characters. Make sure the first couple words are super attention grabbing and that the first sentence is short. Those first couple words need to captivate the reader. Be sensationalist."
            default_summarization_instructions = "Summarize the following article in 480 characters or less:\n\n"
            with open('.env', 'w') as env_file:
                env_file.write("#    put api keys here so they are not exposed to github\n")
                env_file.write(f"OPENAI_API_KEY={api_key}\n")
                env_file.write(f"REDDIT_API_CLIENT_ID={reddit_api_client_id}\n")
                env_file.write(f"REDDIT_API_SECRET={reddit_api_secret}\n")
                env_file.write(f"REDDIT_API_USER_AGENT={reddit_api_user_agent}\n")
                #   give the subreddit options their own setup later
                env_file.write(f"DEFAULT_SUBREDDIT={default_subreddit_to_scrape}\n")
                #   summarize settings
                env_file.write(f"DEFAULT_SUMMARIZATION_CONTEXT={default_summarization_context}\n")
                env_file.write(f"DEFAULT_SUMMARIZATION_INSTRUCTIONS={default_summarization_instructions}\n")
                if default_subreddit_category not in ['top', 'hot', 'new', 'rising']:
                    #   make sure category is valid
                    #   prob should make a class to sanitize input later
                    print(f'{bcolors.RED}Invalid category! Please choose from [top, hot, new, rising].{bcolors.ENDC}')
                    os.copy('.env', '.env-temp')#   make a backup of the .env file before deleting it
                    os.remove('.env')
                    print(f'{bcolors.RED}Setup Failed. Please Make Sure Category is Valid{bcolors.ENDC}')
                    exit()
                else:
                    env_file.write(f"DEFAULT_SUBREDDIT_CATEGORY={default_subreddit_category}\n")
        else:#   if .env file exists, load it
            print(f'{bcolors.ITALICS}Loading Environment Variables...{bcolors.ENDC}')
            load_dotenv()
            print(f'{bcolors.YELLOW}Environment Variables Loaded{bcolors.ENDC}')
        if os.path.exists('.env-temp'):#   delete the autobackup if it exists
            print(f'{bcolors.ITALICS}Autobackup of Environment Variables Detected...{bcolors.ENDC}')
            os.remove('.env-temp')
            print(f'{bcolors.ITALICS}Autobackup of Environment Variables Deleted{bcolors.ENDC}')
    def logfile_exists(self) -> bool:
        return os.path.exists('content/past_articles.json')
    def logfile_setup(self):
        if not self.logfile_exists():
            print(f'{bcolors.ITALICS}No logfile detected...{bcolors.ENDC}')
            os.makedirs('content', exist_ok=True)  # Create the content directory if it doesn't exist
            with open('content/past_articles.json', 'w') as logfile:  # Create an empty logfile
                logfile.write('[]')  # Initialize with an empty JSON array
            print(f'{bcolors.YELLOW}Logfile Created{bcolors.ENDC}')
    def image_directory_exists(self) -> bool:
        return os.path.exists('content/images')
    def image_directory_setup(self):
        if not self.image_directory_exists():
            os.makedirs('content/images', exist_ok=True)# not sure what exist_ok does
            print(f'{bcolors.YELLOW}Images directory created{bcolors.ENDC}')
        else:
            print(f'{bcolors.YELLOW}Images directory already exists{bcolors.ENDC}')
    def test_openai_api_key(self) -> bool:#   check OpenAI API key Validity
        if not self.dotenv_exists():#   make sure the .env file exists
            raise ValueError(f'{bcolors.RED}{bcolors.BOLD}No .env file detected. Please run setup first.{bcolors.ENDC}')
        print(f'{bcolors.ITALICS}Checking API key validity...{bcolors.ENDC}')
        #   check OPENAI API key
        print(f'{bcolors.ITALICS}Checking OPENAI API key...{bcolors.ENDC}')
        test_url = "https://api.openai.com/v1/models"
        openai_api_key = os.getenv('OPENAI_API_KEY')
        headers = {
            "Authorization": f"Bearer {openai_api_key}"
        }
        response = requests.get(test_url, headers=headers)
        try:
            if response.status_code == 200:
                print(f'{bcolors.YELLOW}OPENAI API key is valid.{bcolors.ENDC}')
                return True
            else:
                print(f'{bcolors.BLUE}OPENAI API Key: {openai_api_key}{bcolors.ENDC}')
                raise ValueError(f'{bcolors.RED}Invalid OPENAI API keys. Please check your .env file\n{bcolors.ENDC}{bcolors.HIGHLIGHT}Key: {openai_api_key}{bcolors.ENDC}')
        except ValueError as e:
            print(f'\033[91m{str(e)}\033[0m')
            return False

class bcolors:#   color coding of terminal output
    PINK= '\033[95m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m' 
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    HIGHLIGHT = '\033[100m'
    ITALICS = '\033[3m'
    ENDC = '\033[0m'# gotta use ENDC to terminate color coding
    
#
#   Main Function(s)
#

def start_api():
    from newsbot_api import app
    print(f'{bcolors.YELLOW}Starting API...{bcolors.ENDC}')
    app.run(debug=True)
    pass


def run_on_startup():
    #   do this every time
    if SetupManager().dotenv_exists():
        SetupManager().dotenv_load()#   load the .env file
    else:
        SetupManager().setup_dot_env()
    if not SetupManager().logfile_exists():#   check for logfile
        SetupManager().logfile_setup()#        make logfile if needed

def main():
    print(f'{bcolors.RED}This is a backend module. Please use the CLI to interact with the program.{bcolors.ENDC}')
    print(f'{bcolors.BLUE}{bcolors.ITALICS}Doing it for you...{bcolors.ENDC}')
    os.system('python ./newsbot_cli.py')
    exit()
if __name__ == "__main__":
    main()

