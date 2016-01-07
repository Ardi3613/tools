from mysettings import *
import tweepy

def main():
	auth = tweepy.OAuthHandler(api_key, api_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
	friends = set(tweepy.Cursor(api.friends_ids).items())
	followers = set(tweepy.Cursor(api.followers_ids).items())
	friends -= followers
	if friends:
		print('Unfollowing %d friends' % len(friends))
		for f in friends:
			try:
				res = api.destroy_friendship(user_id=f)
				print(res.screen_name)
			except tweepy.error.TweepError as e:
				print('Error unfollowing user id %d: %s' % (f, e))
	else:
		print('No one to unfollow')

if __name__ == '__main__':
	main()
