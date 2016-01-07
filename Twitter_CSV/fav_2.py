# a keyword to search for, may be provided on command line
search_for = "content"

# limit search to the last tweets for each user
# you can get up to 200 tweets in a single API call
limit_last = 100

# limit total number of fav/rt per script run
limit_total = 5

import sys, re, random
import tweepy
from mysettings import *

if sys.version_info[0] == 2:
	from io import open
	from itertools import imap as map
	str = unicode

def main():
	global search_for
	if len(sys.argv) > 1:
		search_for = sys.argv[1]
	search_for = re.compile(r'\b%s\b' % re.escape(search_for), re.I)
	auth = tweepy.OAuthHandler(api_key, api_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
#	friends = list(tweepy.Cursor(api.friends_ids).items())
	with open(follow_input_file) as f:
		friends = list(map(str.strip, f))
	random.shuffle(friends)
	total = 0
	for user in friends:
#		crs = tweepy.Cursor(api.user_timeline, user_id=user, count=200, trim_user="true", include_rts="false")
		crs = tweepy.Cursor(api.user_timeline, screen_name=user, count=200, trim_user="true", include_rts="false")
		try:
			tweets = [tweet for tweet in crs.items(limit_last) if search_for.search(tweet.text) and not tweet.favorited]
			if tweets:
				tweet = random.choice(tweets)
				tweet.favorite()
#				print('User id %d: favorited' % user)
				print('%s: %s' % (user, tweet.text.encode('ascii', 'replace')))
				total += 1
				if total >= limit_total:
					break
			else:
#				print('User id %d: nothing found' % user)
				print('%s: nothing found' % user)
		except tweepy.error.TweepError as e:
#			print('Error, user id %d: %s' % (user, e))
			print('Error for user %s: %s' % (user, e))

if __name__ == '__main__':
	main()
