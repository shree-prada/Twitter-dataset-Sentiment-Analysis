import snscrape.modules.twitter as snt
import pandas as pd
import re
import emoji
from datetime import date, datetime
from collections import Counter
import csv
import nltk

nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
analyzer=SentimentIntensityAnalyzer()

language_filter = 'lang:en'

#fetching top hashtags from 2 days including today.

start=date.today() #- timedelta(days=1)
#end=datetime.now().strftime("%Y-%m-%d")
print("\nTweets between date range:->Start:",start.strftime("%Y-%m-%d %H:%M:%S"))#," End:",end
keyword=input("\n\nPlease give a keyword for trending tweets-->")

#fetching tweets containing hashtags in date range
Tweets=[]
for tweet in snt.TwitterSearchScraper(f'#{keyword} since:{start} {language_filter}').get_items(): #until:{end} 
   Tweets.append(tweet) 
#print(Tweets)


#fetching only hashtags inside the fetched tweets
hashtags=[]   
for tweet in Tweets:
    for tags in tweet.hashtags:
        hashtags.append(tags.lower())
#print(hashtags)


#frequency count of fetched hashtags
tagFreq=Counter(hashtags)
#print(tagFreq)
retrieved_hashtags=tagFreq.most_common(5)
TopTags=[]
if len(retrieved_hashtags)!=0:
    for tag in range(0,len(retrieved_hashtags),1):
        TopTags.append(retrieved_hashtags[tag][0])
else:
    print("Sorry!! No Tags Associated.")
print(TopTags)


#fetching tweets from finalized top hashtags
final_tweets=[]
for hash in TopTags:
    #print("\n<------>\n",len(final_tweets))
    for tweet in snt.TwitterSearchScraper(f'#{hash} since:{start} {language_filter}').get_items(): # type: ignore #until:{end}
        #print("im in captain!!")
        final_tweets.append(tweet)
#print(final_tweets)
finalDF=pd.DataFrame(final_tweets,columns=["url","date","id","user","replyCount","retweetCount","likeCount","quoteCount","lang","sourceLabel","retweetedTweet","quotedTweet","hashtags","viewCount","renderedContent"])

#replacing "" with NA in retweetedTweets and quotedTweets columns

finalDF.fillna({"retweetedTweet": "NA", "quotedTweet": "NA"}, inplace=True)

TwtwithoutAT=[]
sentimentScore=[]
for tweets in finalDF[['renderedContent'][0]]:
    tweets = re.sub("@+","",tweets) #@[A-Za-z0-9]+
    tweets = re.sub("(?:\\@|http?\\://|https?\\://|www)\\S+","",tweets)
    #emo=str(emoji.emoji_list(tweets))
    #print(emo)
    #tweets = emoji.replace_emoji(tweets,replace=emo)
    tweets = tweets.replace("#", "").replace("_", " ")
    tweets = emoji.replace_emoji(tweets,"")
    tweets = re.sub(r'\n','', tweets).strip() 
    tweets = tweets.replace("\u2019", "'")
    tweets = tweets.replace("\u2018", "'")
    tweets = tweets.replace("\u2026", "...")
    tweets = tweets.replace("\u2013", "-")
    tweets = tweets.replace("\u201c", "\"")
    tweets = tweets.replace("\u201d", "\"")
    
    TwtwithoutAT.append(tweets)
    
    #Sentiment score calculation for polarity comparision.
    sentimentScore.append(analyzer.polarity_scores(tweets))

SentimentVal=[]

for i in sentimentScore:
    if i["compound"]>0:
        SentimentVal.append("Positive")
    elif i["compound"]<0:
        SentimentVal.append("Negative")
    else:
        SentimentVal.append("Neutral")

finalDF['RefinedContent']=TwtwithoutAT
finalDF['SentimentValue']=SentimentVal
finalDF.to_csv("final.csv")


data = finalDF.to_dict(orient='records')