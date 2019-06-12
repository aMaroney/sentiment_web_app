from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import db_connection_secret
import user_tweet_search
import search_db_return_sentiment
import time

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = ''

class ReusableForm(Form):
    name = TextField('Twitter User:', validators=[validators.required()])
    email = TextField('Search Term:', validators=[validators.required(), validators.Length(min=1, max=35)])


@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)

    print(form.errors)
    if request.method == 'POST':
        name=request.form['name']
        search_term=request.form['email']
        print(name, " ", search_term)

        # readable time stamp
        time_stamp = time.ctime()

        # unix time stamp in seconds
        # also the primary key for the search table
        time_stamp_id = int(time.time())

        # Here goes the twitter handle for the user
        # whose tweets are to be extracted.
        # twitter_user = "realDonaldTrump"
        twitter_user = name

        # this is where the search term will go. Current value is just a stand in
        # search_term = 'america'
        search_term = search_term

        # passes the search details to the search table
        execute = ("INSERT INTO "
                   "search_table"
                   "(idsearch_table, search_term, twitter_user, readable_timestamp)"
                   "VALUES (%s,%s,%s,%s)")
        data = time_stamp_id, search_term, twitter_user, time_stamp
        db_connection_secret.dbLocalInsert(execute, data)

        # passes the user to the twitter module for downloading all the users tweets
        user_tweet_search.get_tweets(twitter_user, time_stamp_id)

        # searches the db of all user tweets for the search term and
        # #places those tweets in another table called tweet_search_results
        search_db_return_sentiment.search_keyword_return_sentiment(search_term)


        if form.validate():
            execute = ("SELECT AVG(sentiment_polarity) FROM twitter_sentiment.tweet_search_results"
                       " WHERE idsearch_table = '%s'")  % (time_stamp_id)
            average_sentiment_raw = db_connection_secret.dbLocalPullGeneral(execute)
            average_sentiment = average_sentiment_raw[0][0]
            print(average_sentiment)

            try:
                if average_sentiment >= -1 and average_sentiment < -0.5:
                    sentiment_adj = " - They really don't like it!"
                    flash("Their sentiment on " + search_term + " is " + str(sentiment_adj))
                if average_sentiment >= -0.5 and average_sentiment < 0:
                    sentiment_adj = " - They don't like it!"
                    flash("Their sentiment on " + search_term + " is " + str(sentiment_adj))
                if average_sentiment >= 0 and average_sentiment < 0.5:
                    sentiment_adj = " - They like it!"
                    flash("Their sentiment on " + search_term + " is " + str(sentiment_adj))
                if average_sentiment >= 0.5 and average_sentiment < 1:
                    sentiment_adj = " - They really like it!"
                    flash("Their sentiment on " + search_term + " is " + str(sentiment_adj))
            except Exception as e:
                flash("They don't have an opinion")
                print(e)
        else:
            flash('Error: All the form fields are required. ')

    return render_template('twitter_sentiment_production.html', form=form)

@app.route("/about")
def about():
    return render_template("hello.html")

if __name__ == "__main__":
    app.run()
