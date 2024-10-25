from newsbot_backend import *
import argparse

def parse_shell():
    #   use newsbot like a real command line tool
    parser = argparse.ArgumentParser(description='NewsBot CLI for fetching and managing articles.')
    parser.add_argument('command', choices=['harvest', 'fetch', 'summarize', 'recall','help', 'flask'], 
                        help='Command to execute')
    parser.add_argument('--subreddit', '-s', type=str, 
                        help='Subreddit to scrape articles from')
    parser.add_argument('--category', '-c', type=str, 
                        help='Category to browse [top, hot, new, rising]')
    parser.add_argument('--limit', '-l', type=int, 
                        help='Limit the number of articles fetched')
    parser.add_argument('--url', '-u', type=str, 
                        help='URL of the article to fetch')

    args = parser.parse_args()  # Parse the arguments

    return args.command, args.subreddit, args.category, args.limit, args.url
def exec_command(command, subreddit, category, limit, url):
    #   execute commands based on the command line arguments
    if command == "harvest":
        harvest(subreddit=subreddit, category=category, limit=limit)
    elif command == "fetch":
        if limit is None:
            limit = 1
        for article in fetch_article_from_reddit(subreddit=subreddit, category=category, limit=limit):
            print(article.title)
    elif command == "recall":
        article = recall_article(random=False)
        view_article_summary(article)
    elif command == "help":
        os.system('python ./newsbot_cli.py -h')
    elif command == "flask":
        start_api()
    elif command == 'summarize':
        article = fetch_article_from_url(url)

if __name__ == "__main__":
    run_on_startup() # makes sure the .env file is good to go
    command, subreddit, category, limit, url = parse_shell()#   parse the shell command
    exec_command(command, subreddit, category, limit, url)#   execute the shell command
