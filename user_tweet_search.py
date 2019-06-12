import db_connection_secret
import twitter_credentials


# Function to extract tweets
def get_tweets(username, unix_timestamp):
    #calling api with twitter credintials
    authenticated_twitter_api = twitter_credentials.api

    # 200 tweets to be extracted
    number_of_tweets = 1000

    try:
        tweets = authenticated_twitter_api.user_timeline(screen_name=username, count=number_of_tweets)

        tweets_ids = [tweet.id for tweet in tweets]
        tweet_text = [tweet.text for tweet in tweets]

        #inserting the twitter_user_id into the search table
        #the time stamp will relate the user ID back to the user tweets table so we can store and accumulate user tweets
        for tweet in tweets:
            #parsing through data returned from API call for the twitter user ID
            twitter_user_id = tweet.user.id

            execute = ("UPDATE twitter_sentiment.search_table SET twitter_user_id = %s WHERE idsearch_table = %s")
            data = twitter_user_id, unix_timestamp
            db_connection_secret.dbLocalInsert(execute, data)
            #we're pulling the user ID from the one API call and don't need to iterate through every tweet.
            #we just need to pull the first tweet to obtain the user ID
            break

        # checks to make sure all tweet id's pulled and tweet texts match up based on length of array
        if len(tweets_ids) == len(tweet_text):
            #for individual tweet in array of tweets
            for individual in range(len(tweets_ids)):
                individual_tweet_id = tweets_ids[individual]
                individual_tweet_text = tweet_text[individual]
                #writing all of the tweets to the all_user_tweets table
                execute = ("REPLACE INTO "
                           "all_user_tweets"
                           "(tweet_id, tweet_body, idsearch_table)"
                           "VALUES (%s,%s,%s)")
                data = individual_tweet_id, individual_tweet_text, unix_timestamp
                db_connection_secret.dbLocalInsert(execute, data)

    except Exception as e:
        print(e)
