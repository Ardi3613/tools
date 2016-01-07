# -*- coding: utf-8 *-*
from __future__ import unicode_literals

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *

import getpass
import time
import random
import codecs
import json
import os
import re
import sys
import logging
import csv
import datetime


# version 1.2
# changes
# 1.1
# scraping limit
# save new only
# don't save LinkedIn Member and blank
# 1.2
# bugfix get_previous_results (now ready for with o w/o double quotes)


__doc__ = """

https://www.upwork.com/c/jobs/~01b81630b7bdf66e27

I need all the 'Digital Strategist r digital strategy' and 'media planner' details from New York, US from Linkedin. You can search for these individuals easily enough. There should be about 74,000 digital strategist . Please grab all the details about each person that Linkedin provides.

Out put will be an excel spreadsheet with two tabs.

Also, need original code source for verification and payment.


"""


logging.basicConfig(level=logging.INFO)

MAX_TIMEOUT = 10
DELAY_BETWEEN_PAGES = 20
AUTOATTEMPTS = 2        # attempts to try wait for elem

USE_WEBDRIVER = 'firefox'   # migth be 'firefox' or 'chrome'; 'phantomjs' fails

TEMPDIR = './tmp'
RESULT_FILENAME = 'result'
INCOMING_DATA_CSV_FILE = 'queries.csv'

COL_DELIMITER = b','


class SeleniumMixin():

    def _wait_and_get_elems(self, css_selector, timeout=MAX_TIMEOUT, try_except=True):
        """
        try_except = True: wrap it here
        try_except = False: wrap in in code
        """
        def _get_elems():
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))
            )

        if not try_except:
            # if exception handle it in the main part
            return _get_elems()
        else:
            while 1:
                # 3? times to auto find element at the page, then manually
                for t in range(AUTOATTEMPTS):
                    try:
                        while 1:
                            # 3? times auto then manual for "is any elem displayed?"
                            for i in range(AUTOATTEMPTS):
                                # TimeoutException if elem not appears while MAX_TIMEOUT
                                elems = _get_elems()
                                # check for visible
                                # if not visible then click() function will fails

                                #--- any elem displayed?
                                if reduce(lambda x, y: x or y, [elem.is_displayed() for elem in elems]):
                                    return elems
                                else:
                                    logging.warning('{0} displayed: {1}'.format(css_selector, elems[0].is_displayed()))
                                    logging.warning('Autoretry during {0} seconds'.format(self.max_timeout/2))
                                    time.sleep(self.max_timeout/2)
                                    continue

                            logging.warning('{0} not displayed'.format(css_selector))
                            #s = raw_input('Wait for display and press Enter key (preferred) or enter Q to return in main loop (may shut down the script with exception): ', )
                            logging.warning('Elems not found. Return False')
                            s = 'Q'     # hard coded Quit
                            if re.findall('(?i)[QqЙй]', s):
                                # quit and return to main loop
                                return
                            # still try for is_displayed = True
                            continue
                    except:
                        logging.warning("Problem with getting {0}. Element doesn't exist".format(css_selector))
                        logging.warning('Autoretry during {0} seconds'.format(self.max_timeout/2))
                        time.sleep(self.max_timeout/2)
                        continue

                logging.warning("Problem with getting {0}. Element doesn't exist".format(css_selector))
                logging.warning(sys.exc_info()[0])
                # s = raw_input('Wait for element and press Enter key (preferred) or enter Q to return in main loop (may shut down the script with exception): ', )
                s = 'Q'     # hard coded Quit
                logging.warning('Elems not found. Return False')
                if re.findall('(?i)[QqЙй]', s):
                    # quit and return to main loop
                    return

    def get_text(self, elem):
        try:
            text = (elem.text or elem.get_attribute('innerHTML')).strip()
        except:
            text = "ERROR. {0}".format(sys.exc_info())  # todo improve it
        return text

    def get_elem_data(self, parent, css_selector):
        elems = parent.find_elements_by_css_selector(css_selector)
        if elems:
            return self.get_text(elems[0])
        else:
            return ''

class LinkedInScraper(SeleniumMixin, object):

    def __init__(self, login='', password='', scraping_depth=0, tempdir=TEMPDIR, result_filename=RESULT_FILENAME,
                 incoming_data_csv_file=INCOMING_DATA_CSV_FILE, csv_delimiter=COL_DELIMITER, search_for=None,
                 use_webdriver=USE_WEBDRIVER, max_timeout=MAX_TIMEOUT):

        if not search_for:
            search_for = {}

        self.login = login
        self.password = password

        self.scraping_depth = int(scraping_depth)

        self.tempdir = tempdir
        self.result_filename = result_filename
        self.result_filepath = os.path.join(self.tempdir, self.result_filename)
        self.incoming_data_csv_file = incoming_data_csv_file
        self.csv_delimiter = csv_delimiter

        self.search_for = search_for
        self.max_timeout = max_timeout

        self.create_dir()
        # commented to add in previous results
        # self.create_file()
        self.previous_results_urls = self.get_previous_results()

        self.driver = self.init_webdriver(use_webdriver)
        self.item_counter = 1
        self.query_counter = 0

        self.result = []

        self.login_linkedin()
        self.main_scraper()

        self.json_result = json.dumps(self.result)

    @staticmethod
    def init_webdriver(use_webdriver):
        if use_webdriver == 'phantomjs':
            driver = webdriver.PhantomJS()
            # driver = webdriver.PhantomJS(desired_capabilities=webdriver.DesiredCapabilities.PHANTOMJS)
        elif use_webdriver == 'chrome':
            driver = webdriver.Chrome()
        else:
            # default
            driver = webdriver.Firefox()
        return driver

    def save_item_to_file(self, JSON_profile):
        """
        :param JSON_profile: dict, not json string
        """
        with codecs.open("{}.txt".format(self.result_filepath), 'a', 'utf-8') as j:
            j.write(json.dumps(JSON_profile, indent=4, sort_keys=True))

        with codecs.open("{}.csv".format(self.result_filepath), 'a', 'utf-8') as c:
            c.write('"{Name}","{Title}","{URL}"\n'.format(**JSON_profile['Person']))

        with codecs.open('log.txt', 'a', 'utf-8') as l:
            l.write(JSON_profile['Person']['Name'] + ', SUCCESS\n')

        logging.info("{} data saved".format(JSON_profile['Person']['Name']))

    def get_previous_results(self):
        # url is last column in csv
        logging.info("get previous results")
        with codecs.open("{}.csv".format(self.result_filepath), 'r', 'utf-8') as c:
            members_urls = [re.findall('http.*?$', l)[0].strip('"') for l in c.readlines() if 'http' in l]
        logging.info("got previous results")
        return members_urls

    def create_dir(self):
        if not os.path.exists(self.tempdir):
            # was renamed
            os.makedirs(self.tempdir)

    def create_file(self):
        with codecs.open("{}.txt".format(self.result_filepath), 'w', 'utf-8') as f:
            pass
        with codecs.open("{}.csv".format(self.result_filepath), 'w', 'utf-8') as f:
            pass
        return

    def login_linkedin(self):
        logging.info('login')
        self.driver.get('https://www.linkedin.com/')
        time.sleep(1)
        #-- login
        is_loaded = self._wait_and_get_elems('#session_key-login')
        self.driver.find_element_by_css_selector('#session_key-login').send_keys(self.login)
        self.driver.find_element_by_css_selector('#session_password-login').send_keys(self.password)
        time.sleep(1)
        self.driver.find_element_by_css_selector('#signin').click()
        time.sleep(5)
        logging.info('login successful')

    def get_people_scraper_item_data_from_list(self, item):
        """
        get item details for range scraper
        """
        vcard = item
        # Create custom JSON profile file and save it
        JSON_profile = {'Person': {}}

        # Get given name
        JSON_profile['Person']['Name'] = self.get_elem_data(vcard, 'h3 a.title')

        # don't save: hidden member
        if not JSON_profile['Person']['Name'] or JSON_profile['Person']['Name'] == "LinkedIn Member":
            return None, 'closed profile'

        # Get search request url
        JSON_profile['Person']['Request URL'] = self.driver.current_url

        # Get profile URL
        JSON_profile['Person']['URL'] = ''
        urls = vcard.find_elements_by_css_selector('h3 a.title')
        if urls:
            # clear from session data
            cleared_urls = re.findall('^.*?id=\d+', urls[0].get_attribute('href'))
            if cleared_urls:
                JSON_profile['Person']['URL'] = cleared_urls[0]
            else:
                JSON_profile['Person']['URL'] = urls[0]

        # don't save: repeated
        if JSON_profile['Person']['URL'] in self.previous_results_urls:
            return None, '{} already scraped'.format(JSON_profile['Person']['Name'])

        # MemberId and Public Profile
        try:
            member_id = (
                re.findall('profile/(\d+)', JSON_profile['Person']['URL'])
                or
                re.findall('profile/view\?id=(\d+)', JSON_profile['Person']['URL'])
                or
                re.findall('people/show/(\d+)', JSON_profile['Person']['URL'])
            )[0]
        except IndexError:
            member_id = 'ERROR'
        JSON_profile['Person']['Member ID'] = member_id
        JSON_profile['Person']['Public Link'] = \
            'https://www.linkedin.com/profile/view?id={0}'.format(
                JSON_profile['Person']['Member ID']
            )
        #public_links = self.driver.find_elements_by_css_selector('li.public-profile a')
        #JSON_profile['Person']['Public Link'] = public_links[0] if public_links else ''

        # Get network degree
        JSON_profile['Person']['Network Degree'] = self.get_elem_data(vcard, '.degree-icon')    # ok
        # Get Title
        JSON_profile['Person']['Title'] = self.get_elem_data(vcard, '.description')         # ok
        # Get Location
        JSON_profile['Person']['Location'] = self.get_elem_data(vcard, '.demographic bdi')  # ok
        # Get Industry
        try:
            JSON_profile['Person']['Industry'] = vcard.find_elements_by_css_selector('.demographic dd')[1].text # ok
        except IndexError:
            JSON_profile['Person']['Industry'] = ''

        # Get Keywords
        JSON_profile['Person']['Keywords'] = 'Not presented'

        # Save
        self.save_item_to_file(JSON_profile)
        return JSON_profile, None

    def page_people_scraper(self):
        """
        scraper for query
        https://www.linkedin.com/cap/peopleSearch/resultsWithFacets/916899773?savedSearchId=69342773#facets=savedSearchId%3D69342773%26searchHistoryId%3D916899773%26savedSearchName%3Dgoogle-final%26resultsType%3Dsearch%26sortCriteriaCode%3DR%26internalCandidatesOnly%3Dfalse%26keywords%3Dgoogle%26firstName%3D%26lastName%3D%26jobTitle%3D%26company%3D-%2520Google%2520AND%2520-%2520Amazon%2520AND%2520-%2520Microsoft%2520AND%2520-%2520Apple%26school%3D%26userSearchId%3D%26companyTimeSelection%3DC%26locationType%3DANY%26facet.PC%3D1441%26facet.CS%3D8%26facet.SE%3D10%25209%25208%25207%25206%25205%26openFacets%3DPC%252CCS%252CSE%26trackingSearchOrigin%3DSRSB%26noSpellCheck%3Dfalse%26count%3D0
        """

        result_counters = self._wait_and_get_elems('#results_count strong')
        if result_counters[0].text == '0':
            # no results
            logging.info('No results')
            time.sleep(0.5 + random.random())
            return

        items_selector = 'li.result'
        logging.info('wait..')
        time.sleep(DELAY_BETWEEN_PAGES+random.random()*2)   # wait for update persons page and wait page delay

        items = self._wait_and_get_elems(items_selector)
        items = items or []

        logging.info('got {0} person(s) at the list page'.format(len(items)))
        for item in items:
            json_profile, err = self.get_people_scraper_item_data_from_list(item)
            if err:
                logging.info("not saved: {}".format(err))
                continue

            logging.debug(json_profile)

            self.item_counter += 1
            self.result.append(json_profile)

    def main_scraper(self):

        with open(self.incoming_data_csv_file, 'r') as f:
            if not self.scraping_depth:
                logging.info('scraping depth: unlimited pages per query')
            else:
                logging.info('scraping depth: {} page(s) per query'.format(self.scraping_depth))
            reader = csv.reader(f, dialect='excel', delimiter=self.csv_delimiter)
            for line in reader:
                self.search_for = line[0].strip()
                self.query_counter += 1
                logging.info('{0}:\tsearch for {1}'.format(self.query_counter, self.search_for))

                #-- request
                logging.info('open init page')
                self.driver.get(self.search_for)
                logging.info('init page opened')

                #-- page iterator
                self.page_num = 1
                while 1:
                    # check scraping depth

                    self.page_people_scraper()
                    self.page_num += 1
                    # check depth
                    if self.scraping_depth and self.page_num > self.scraping_depth:
                        logging.info('depth (pages):{} ; next page:{}'.format(self.scraping_depth, self.page_num))
                        logging.info('break on scraping limit, go to next query')
                        break
                    delay = DELAY_BETWEEN_PAGES/2 + random.random()*DELAY_BETWEEN_PAGES
                    logging.info('delay {} secs'.format(delay))
                    time.sleep(delay)   # some delay
                    try:
                        nextlink = self.driver.find_element_by_link_text('Next >')
                        nextlink.click()
                        logging.info('open page {}'.format(self.page_num))
                    except NoSuchElementException:
                        logging.info('no more pages with result, go to next query')
                        break
            logging.info('no more queries. exit')


    def __del__(self):
        self.driver.close()
        self.driver.quit()


def test():

    print '------ start ------- {0}'.format(datetime.datetime.now())

    login = raw_input('Login: ')
    passw = getpass.getpass('Passowrd: ')
    scraping_depth = raw_input('Scraping depth limit (pages per query, inf if blank): ') or 0

    li = LinkedInScraper(
        login=login,
        password=passw,
        scraping_depth=scraping_depth
    )

    print li.json_result
    print '------ finish ------- {0}'.format(datetime.datetime.now())


if __name__ == "__main__":
    test()