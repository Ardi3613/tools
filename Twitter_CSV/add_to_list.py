# list to add users to, may be provided as command-line parameter
list_slug = "dal-mba-peeps"

import sys
from itertools import chain, islice
import tweepy
from mysettings import *

if sys.version_info[0] == 2:
	from io import open
	from itertools import imap as map
	str = unicode

def chunker(seq, n):
	it = iter(seq)
	while True:
		yield chain((next(it),), islice(it, n-1))

def main():
	global list_slug
	if len(sys.argv) > 1:
		list_slug = sys.argv[1]
	with open(follow_input_file) as f:
		auth = tweepy.OAuthHandler(api_key, api_secret)
		auth.set_access_token(access_token, access_token_secret)
		api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
		owner = auth.get_username()
		for n, chunk in enumerate(chunker(map(str.strip, f), 100), 1):
			try:
				api.add_list_members(screen_name=chunk, slug=list_slug, owner_screen_name=owner)
				print('Added %d users' % (n*100))
			except tweepy.error.TweepError as e:
				print('Error: %s' % e)

if __name__ == '__main__':
	main()
