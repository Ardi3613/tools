# -*- coding: utf-8 -*-

''' 
Requirements:

https://github.com/bufferapp/buffer-python
https://bufferapp.com/developers/apps/create


Copyright Programming for Marketers, Nathaniel Eliason, 2015
Free for use with attribution
'''

'''
To do:

- Add code for other profiles
- Add "promo category"
- Other categories as necessary, show them how to add one

'''


from buffpy.managers.profiles import Profiles
from buffpy.managers.updates import Updates
from buffpy.api import API
from bufferinfo import *
from quote_bot_quotes import *
import random

api = API(client_id=CLIENTID,
          client_secret=CLIENTSECRET,
          access_token=ACCESSTOKEN)

profile = Profiles(api=api).filter(service='twitter')[0]


def test_code():
	profiles = Profiles(api=api)
	print profiles.all

if __name__ == "__main__":
	test_code()


'''
def add_to_buffer(count):
	bufferQuotes = random.sample(quotes, count)

	for j in bufferQuotes:
		try:
			profile.updates.new(j, now=False)
		except:
			add_to_buffer(1)

if __name__ == "__main__":
	add_to_buffer(3)
'''