import db_connection_secret
from textblob import TextBlob

def search_keyword_return_sentiment(search_term):
    #search term input from user
    search_term_original = search_term

    #modifying the user search term by adding '%' so that I can use LIKE in my sql query
    search_term_for_db = '%'+search_term_original+'%'

    #sql query that take in a variable
    execute = ("SELECT tweet_id, tweet_body, all_user_tweets.idsearch_table FROM twitter_sentiment.all_user_tweets "
                "JOIN twitter_sentiment.search_table ON all_user_tweets.idsearch_table = search_table.idsearch_table "
               "WHERE tweet_body LIKE '%s'")  % (search_term_for_db)

    #this bit of code isn't being used at the moment
    # data = search_term_for_db
    # db_connection_secret.dbLocalPullExact(execute, data)

    #executing the sql query
    search_results = db_connection_secret.dbLocalPullGeneral(execute)
    for tweet in search_results:
        tweet_id = tweet[0]
        tweet_body = tweet[1]
        idsearch_table = tweet[2]

        #returns sentiment on users tweet
        to_TextBlob = TextBlob(tweet_body)
        sentiment_polarity = to_TextBlob.sentiment.polarity
        sentiment_subjectivity = to_TextBlob.sentiment.subjectivity

        #places data from the funtion into the tweet_search_results table
        execute = ("REPLACE INTO "
                   "tweet_search_results"
                   "(tweet_id, idsearch_table, sentiment_polarity, sentiment_subjectivity, tweet_body)"
                   "VALUES (%s,%s,%s, %s,%s)")
        data = tweet_id, idsearch_table, sentiment_polarity, sentiment_subjectivity, tweet_body
        db_connection_secret.dbLocalInsert(execute, data)


'''
The sentiment property returns a namedtuple of the form Sentiment(polarity, subjectivity). 
The polarity score is a float within the range [-1.0, 1.0]. 
The subjectivity is a float within the range [0.0, 1.0] where 0.0 is very objective and 1.0 is very subjective.
'''