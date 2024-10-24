from flask import Flask, request, jsonify
from newsbot_backend import recall_article, recall_all_articles, harvest


app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'message': 'Hello, World!'})

@app.route('/api/retrieve-latest-article', methods=['GET'])
# Retrieve the latest article
def retrieve_latest_article():
    article = recall_article()  # Call the recall function to get the article
    if article:
        return jsonify({'summary': article.summary, 'link': article.url})  # Return the summary and link as JSON
    else:
        return jsonify({'summary': 'No article found.'}), 404

@app.route('/api/retrieve-all-articles', methods=['GET'])
# Retrieve all articles
def retrieve_all_articles():
    articles = recall_all_articles()  # Call the function to get all articles
    if articles:
        return jsonify([{'title': article.title, 'summary': article.summary} for article in articles])  # Return all articles as JSON
    else:
        return jsonify({'message': 'No articles found.'}), 404

@app.route('/api/scrape-and-retrieve', methods=['POST'])
def scrape_and_retrieve():
    subreddit = request.json.get('subreddit', None)  # Default to None if not provided
    category = request.json.get('category', None)    # Default to None if not provided
    limit = request.json.get('limit', None)          # Default to None if not provided

    harvest()


if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)

