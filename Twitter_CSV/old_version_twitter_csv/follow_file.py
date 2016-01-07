import sys
import tweepy
from mysettings import *

def main():
	if len(sys.argv) > 1:
		input_file_name = sys.argv[1]
	else:
		input_file_name = follow_input_file
	with open(input_file_name) as f:
		auth = tweepy.OAuthHandler(api_key, api_secret)
		auth.set_access_token(access_token, access_token_secret)
		api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
		for user in f:
			user = user.strip()
			try:
				res = api.create_friendship(screen_name=user)
				print(res.screen_name)
			except tweepy.error.TweepError as e:
				print('Error following %s: %s' % (user, e))

if __name__ == '__main__':
	main()
