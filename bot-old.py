
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
from newspaper import Article# newspaper3k article parsing
import requests#   import requests to send post request to openai
import json #   for logfile
import time#   for date stamping in logfile
#
#       Classes
#


class bcolors:#   class for color coding terminal output
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
#       setup functions
#

def setup_dot_env():#   environment variable load and setup, api key loading
    print(f'{bcolors.ITALICS}Checking Environment Variables...{bcolors.ENDC}')
    #   if .env file does not exist, create it, save api key to it and test keys
    if not os.path.exists('.env'):
        print(f'{bcolors.ITALICS}{bcolors.PINK}Entering First Time Setup...{bcolors.ENDC}')
        api_key = input(f'{bcolors.BLUE}Enter OPENAI API KEY: {bcolors.ENDC}')
        default_subreddit_to_scrape = input(f'{bcolors.BLUE}Enter Default Subreddit to Scrape: {bcolors.ENDC}')
        reddit_api_client_id = input(f'{bcolors.BLUE}Enter Reddit API Client ID: {bcolors.ENDC}')
        reddit_api_secret = input(f'{bcolors.BLUE}Enter Reddit API Secret: {bcolors.ENDC}')
        reddit_api_user_agent = input(f'{bcolors.BLUE}Enter Reddit API User Agent: {bcolors.ENDC}')
        with open('.env', 'w') as env_file:
            env_file.write("# put api keys here so they are not exposed to github\n")
            env_file.write(f"OPENAI_API_KEY={api_key}\n")
            env_file.write(f"REDDIT_API_CLIENT_ID={reddit_api_client_id}\n")
            env_file.write(f"REDDIT_API_SECRET={reddit_api_secret}\n")
            env_file.write(f"REDDIT_API_USER_AGENT={reddit_api_user_agent}\n")
            env_file.write(f"DEFAULT_SUBREDDIT={default_subreddit_to_scrape}\n")
        load_dotenv()
        print(f'{bcolors.ITALICS}Saving Environment Variables to .env...{bcolors.ENDC}')
        test_api_keys()
        #print(f'{bcolors.BLUE}{bcolors.BOLD}Setup Complete. Run script again to generate tweets.{bcolors.ENDC}')
    else:#   if .env file exists, load it
        load_dotenv()
        print(f'{bcolors.YELLOW}Environment Variables Loaded{bcolors.ENDC}')
        print(f'{bcolors.BLUE}Default Subreddit to Scrape: {bcolors.BOLD}{os.getenv("DEFAULT_SUBREDDIT")}{bcolors.ENDC}')
        return True
    
def test_api_keys():#   check API key Validity
    print(f'{bcolors.ITALICS}Checking API key validity...{bcolors.ENDC}')
    #   check OPENAI API key
    print(f'{bcolors.ITALICS}Checking OPENAI API key...{bcolors.ENDC}')
    test_url = "https://api.openai.com/v1/models"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }
    response = requests.get(test_url, headers=headers)
    try:
        if response.status_code == 200:
            print(f'{bcolors.YELLOW}OPENAI API key is valid.{bcolors.ENDC}')
            openai_api_key_valid = True
        else:
            raise ValueError(f'{bcolors.RED}Invalid OPENAI API keys. Please check your .env file.{bcolors.ENDC}')
            openai_api_key_valid = False
    except ValueError as e:
        print(f'\033[91m{str(e)}\033[0m')
        openai_api_key_valid = False
    #   can't figure out how to test Reddit API key, so skipping for now

def setup_content_folders():#   create folders for content if they dont exist
    print(f'{bcolors.ITALICS}Checking content folders...{bcolors.ENDC}')
    if not os.path.exists('content'):
        print(f'{bcolors.ITALICS}Creating content folders...{bcolors.ENDC}')
        os.makedirs('content')#   folder for all generated content
        os.makedirs('content/summaries')#   folder for all summaries
        os.makedirs('content/audios')#   folder for all audio files
        os.makedirs('content/images')#   folder for all images
        os.makedirs('content/videos')#   folder for all videos
        os.makedirs('content/subtitles')#   folder for all subtitles
    else:
        print(f'{bcolors.YELLOW}Content folder exists{bcolors.ENDC}')

def setup_article_logfile():  # make sure logfile exists
    print(f'{bcolors.ITALICS}Checking article logfile...{bcolors.ENDC}')
    logfile_path = 'content/article_logfile.json'
    if not os.path.exists(logfile_path):  # if logfile doesn't exist, create it
        print(f'{bcolors.ITALICS}Creating article logfile...{bcolors.ENDC}')
        with open(logfile_path, 'w') as logfile:
            json.dump([], logfile)  # initialize with an empty list
    else:
        print(f'{bcolors.YELLOW}Article logfile exists{bcolors.ENDC}')
        return True  # return true if file exists
#
#       Helper Functions
#

def is_url_reachable(url):#   check if url is valid
    print(f'{bcolors.ITALICS}URL : {url}{bcolors.ENDC}')
    print(f'{bcolors.ITALICS}Testing URL for connection...{bcolors.ENDC}')
    try:
        response = requests.get(url)
        print(f'{bcolors.YELLOW}Connection Successful{bcolors.ENDC}')
        return response.status_code == 200
    except requests.exceptions.RequestException:
        print(f'{bcolors.RED}Could not connect to URL: {url}{bcolors.ENDC}')
        return False

def is_article_novel():  # check if article has been used before
    global titles_and_links  # access the dictionary of posts
    print(f'{bcolors.ITALICS}Checking if article is novel...{bcolors.ENDC}')
    with open('content/article_logfile.json', 'r') as logfile:
        articles = json.load(logfile)
        existing_links = {article["ARTICLE_LINK"] for article in articles}  # Collect existing ARTICLE_LINKs
        titles_to_remove = []  # List to hold titles of articles to remove
        for title, link in titles_and_links.items():  # Iterate directly over the dictionary
            if link in existing_links:
                print(f'{bcolors.RED}Article already logged: {bcolors.ENDC}{bcolors.ITALICS}{" ".join(title.split()[:3])}...{bcolors.ENDC}')
                titles_to_remove.append(title)  # Add title to removal list
        for title in titles_to_remove:  # Remove titles after iteration
            del titles_and_links[title]
        return bool(titles_and_links)# True is titles_and_links has contents, which are only novel ones 

def log_article():#   log article to logfile
    global titles_and_links#   access the dictionary of posts
    article_logfile_path = 'content/article_logfile.json'  # code is used twice, maybe make a global variable
    novel_article_title = next(iter(titles_and_links))
    print(f'{bcolors.BLUE}Article is not  logged: {bcolors.ENDC}{" ".join(novel_article_title.split()[:3])}...')
    print(f'{bcolors.ITALICS}Logging article...{bcolors.ENDC}')
    with open(article_logfile_path, 'r+') as logfile:
        articles = json.load(logfile)
        existing_ids = {article["ARTICLE_ID"] for article in articles}  # Collect existing ARTICLE_IDs
        article_id = 0  # Start from 0 for unique ID assignment
        for title, link in titles_and_links.items():
            while article_id in existing_ids:  # Ensure the article_id is unique
                article_id += 1
            articles.append({
                "ARTICLE_ID": article_id,#   unique ID for each article. prob not needed, use link instead. nicely readable tho.
                "ARTICLE_TITLE": title,
                "ARTICLE_LINK": link,
                "DATE": int(time.time())  # Non-human readable date stamp of when article was scraped
            })
            article_id += 1  # Increment the article ID for the next entry
        logfile.seek(0)
        json.dump(articles, logfile, indent=4)
        print(f'{bcolors.YELLOW}Article logged{bcolors.ENDC}')


#
#       Scraping Functions
#

#   pull the first rising post from default subreddit with praw
def scrape_subreddit(how_many_posts=1):
    #   get default subreddit to scrape from .env
    sub_to_scrape = os.getenv("DEFAULT_SUBREDDIT")
    #   what category to pull from?
    subreddit_category = "rising"
    #   how many posts to pull?
    number_of_posts= how_many_posts
    #   initialize praw with api keys
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_API_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_API_SECRET"),
        user_agent=os.getenv("REDDIT_API_USER_AGENT"),
    )
    #   initialize dictionary to hold titles and links
    titles_and_links = {}
    #   get posts from subreddit using praw
    for submission in getattr(reddit.subreddit(sub_to_scrape), subreddit_category)(limit=number_of_posts):
        titles_and_links[submission.title] = submission.url
    #   dictionary is used so that more than one post can be pulled if wanted
    if titles_and_links:
        first_title = next(iter(titles_and_links))
    else:
        print("No Posts Found")
    return titles_and_links

def scrape_until_novel():
    global titles_and_links
    print(f'{bcolors.ITALICS}{bcolors.HIGHLIGHT}Initiating Scraping...{bcolors.ENDC}')
    #   loop until a novel article is found
    iteration_count = 1#   sets the loop timer
    search_depth = 1#   increasingly searches deeper in the results
    while iteration_count < 2:
        #for title in titles_and_links.keys():
            #print(f'{bcolors.RED}{title}{bcolors.ENDC}')  # Output each title on its own line
        if is_article_novel():# article is novel, and summarize
            log_article()#   log article to logfile
            print(f'{bcolors.ITALICS}Summarizing article...{bcolors.ENDC}')
            output_summary, output_link = summarize_article()# call summarize_article
            #print(f'{bcolors.YELLOW}{bcolors.BOLD}{output_summary}{bcolors.ENDC}') 
            log_summary(output_summary,output_link)# log summary to logfile
            iteration_count += 1#   increment iteration count, stopping it
            search_depth = 1
        else:#   keep digging
            print(f'{bcolors.ITALICS}{bcolors.HIGHLIGHT}Scraping New Article...{bcolors.ENDC}')
            search_depth += 1
            titles_and_links = scrape_subreddit(search_depth)#   scrape subreddit deeper

#
#       Summarizing Functions
#

def summarize_article():
    global titles_and_links # access the dictionary of posts
    # Iterate through the titles_and_links dictionary and output the first article's link entry
    for title, link in titles_and_links.items():
        print(f'{bcolors.BLUE}URL : {bcolors.ENDC}{bcolors.ITALICS}{link}{bcolors.ENDC}')  # Output the link of the first article
        article = Article(link)
        article.download()
        article.parse()
        content = article.text
        break  # Exit after the first entry
    #   use openai to summarize article
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a twitter journalist that summarizes articles and realys them to adoring fans. Have a dry sense of humor. Focus on being clear in communication. Keep all responses under 480 characters. Make sure the first couple words are super attention grabbing and that the first sentence is short. Those first couple words need to captivate the reader. Be sensationalist."},
            {"role": "user", "content": f"Summarize the following article in 480 characters or less:\n\n{content}"}
        ]
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    
    if response.status_code == 200:
        print(f'{bcolors.YELLOW}Article Summarized{bcolors.ENDC}')
        return response.json()['choices'][0]['message']['content'].strip(), link
    else:
        return f"Error: {response.status_code} - {response.text}"

def log_summary(summary, article_link):
    # Log the summary to the logfile
    global titles_and_links
    logfile_path = 'content/article_logfile.json'
    print(f'{bcolors.ITALICS}Logging summary...{bcolors.ENDC}')
    print(f'{bcolors.BLUE}{summary}{bcolors.ENDC}')
    # Load existing articles from the logfile
    with open(logfile_path, 'r') as file:
        articles = json.load(file)
    
    # Find the article with the matching link and add the summary
    for article in articles:
        if article['ARTICLE_LINK'] == article_link:
            article['SUMMARY'] = summary
            break
    
    # Write the updated articles back to the logfile
    with open(logfile_path, 'w') as file:
        json.dump(articles, file, indent=4)
    print(f'{bcolors.YELLOW}Summary Logged{bcolors.ENDC}')

#
#   Main Function(s)
#

def main():
    global titles_and_links  #  access global variable
    setup_dot_env()#   create or load .env API keyfile
    setup_content_folders()#   create content folders
    setup_article_logfile()#   create article logfile
    titles_and_links = scrape_subreddit()#   define global variable
    scrape_until_novel()#   do the thing(scrape, evaluate, summarize, save)


#   run main function if script is executed directly
#   doesnt run if imported as a module
if __name__ == "__main__":
    main()
