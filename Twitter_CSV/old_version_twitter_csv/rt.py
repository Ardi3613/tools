# a keyword to search for, may be provided on command line
search_for = "a16z"

# limit search to the last tweets for each user
# you can get up to 200 tweets in a single API call
limit_last = 100

# limit total number of fav/rt per script run
limit_total = 5

import sys, re, random
import tweepy
from mysettings import *

def main():
	global search_for
	if len(sys.argv) > 1:
		search_for = sys.argv[1]
	search_for = re.compile(r'\b%s\b' % re.escape(search_for), re.I)
	auth = tweepy.OAuthHandler(api_key, api_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
	friends = list(tweepy.Cursor(api.friends_ids).items())
	random.shuffle(friends)
	total = 0
	for user in friends:
		crs = tweepy.Cursor(api.user_timeline, user_id=user, count=200, trim_user="true", include_rts="false")
		try:
			tweets = [tweet for tweet in crs.items(limit_last) if search_for.search(tweet.text) and not tweet.retweeted]
			if tweets:
				tweet = random.choice(tweets)
				tweet.retweet()
				print('User id %d: retweeted' % user)
				total += 1
				if total >= limit_total:
					break
			else:
				print('User id %d: nothing found' % user)
		except tweepy.error.TweepError as e:
			print('Error, user id %d: %s' % (user, e))

if __name__ == '__main__':
	main()
