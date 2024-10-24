from newsbot_backend import *
import argparse

def parse_shell():
    #   use newsbot like a real command line tool
    parser = argparse.ArgumentParser(description='NewsBot CLI for fetching and managing articles.')
    parser.add_argument('command', choices=['harvest', 'fetch', 'summarize', 'recall','help', 'api', 'setup'], 
                        help='Command to execute')
    parser.add_argument('--subreddit', '-s', type=str, 
                        help='Subreddit to scrape articles from')
    parser.add_argument('--category', '-c', type=str, 
                        help='Category to browse [top, hot, new, rising]')
    parser.add_argument('--limit', '-l', type=int, 
                        help='Limit the number of articles fetched')

    args = parser.parse_args()  # Parse the arguments
    return args.command, args.subreddit, args.category, args.limit

def exec_command(command, subreddit, category, limit):
    #   execute commands based on the command line arguments
    if command == "harvest":
        harvest(subreddit=subreddit, category=category, limit=limit)
    elif command == "fetch":
        if limit is None:
            limit = 1
        for article in fetch_article_from_reddit(subreddit=subreddit, category=category, limit=limit):
            print(article.title)
    elif command == "summarize":
        article = recall_article()
        view_article_summary(article)
    elif command == "recall":
        article = recall_article(random=False)
        view_article_summary(article)
    elif command == "help":
        os.system('python ./newsbot_cli.py -h')
    elif command == "api":
        start_api()
    elif command == "setup":
        #   sets up .env even if it exists 
        confirm = input("This will delete all API keys and default settings. Are you sure you want to continue? (y/N): ").strip().lower()
        if confirm == 'y':
            SetupManager().first_time_setup()
        else:
            print("Operation Cancelled.")
        

if __name__ == "__main__":
    run_on_startup() # makes sure the .env file is good to go
    command, subreddit, category, limit = parse_shell()#   parse the shell command
    exec_command(command, subreddit, category, limit)#   execute the shell command