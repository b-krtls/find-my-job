"""
    [summary]

[extended_summary]

:TODO:
- [ ] Write Module Docstring
- [ ] Remove unused imports
- [ ] Use Logger for logging execution
- [ ] Check Style for compatibility with PEP 8, 257 and 484 
"""

import os
import sys
import platform
import time
import argparse
import configparser
import time  # Possibly unused
import urllib.parse
import logging
import asyncio  # Possibly unused
import re
import csv
from bs4 import BeautifulSoup, element
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver # Potentially unused
from selenium.webdriver.common.keys import Keys
from pprint import pprint  # Pretty-printer for testing
from typing import Iterable, Sequence, Union


logger = logging.getLogger(__name__)

def parse_cli_inputs():

    argparser = argparse.ArgumentParser()
    group = argparser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f", "--file",
        dest="file",
        help="Execute the script from a config file",
    )
    group.add_argument(
        "-s", "--single",
        help="Execute the script for singular arguments",
        default=NotImplemented,
    )
    argparser.add_argument(
        "--headless",
        help="Run WebDriver in headless mode",
        action="store_true",
        default=False, 
    )
    argparser.add_argument(
        "--incognito",
        help="Run WebDriver in incognito mode",
        action="store_true",
        default=False,
    )
    argparser.add_argument(
        "--log",
        help="Log the execution history in current working directory",
        action="store_true",
        default=False,
    )
    CLI_ARGS = argparser.parse_args()


class ConfigHandler:
    
    def __init__(self, filename: str, mode: str) -> None:

        allowed_modes = {"generate", "resolve", "help"}
        mode_switcher = {
            "generate": self._generate_bare_bones_config,
            "resolve": self._interpret_configuration_file,
            "help": ...  # :REVIEW:  is Ellipsis correct in this case?
        }

        self.filename = filename

        if mode.casefold() not in allowed_modes:
            raise ValueError("mode='{}': It is not a permitted mode for {}"\
                .format(mode, self.__class__.__name__))
        else:
            self.mode = mode
    
        mode_switcher[self.mode](self.filename)

    def _interpret_configuration_file(filename):

        # Use configparser to obtain information from given config file.
        config = configparser.ConfigParser()
        config.read(filename)

        return config

    def _generate_bare_bones_config(filepath):
        #:FIXME:
        pass
    
    def _generate_example_config(filepath):
        # :FIXME:
        pass

class JobSearcher:
    #:TODO:
    # [ ] Implement __str__ or at least __repr__ dunder methods

    def __init__(self, config: configparser.ConfigParser) -> None:
        self.config = config
        self.website = config["website"].casefold()
        self.keywords = config["keywords"].casefold()
        self.keywords_quoted = ""
        self.location = config["location"].casefold()
        self.location_quoted = ""
        self.url = ""

        self._form_search_url()

    def _form_search_url(self):
        
        if self.website == 'linkedin':
            # :FIXME:
            #  Search URL is hardcoded to be for LinkedIn, fix this
            #       to be conditional according to  config file
            # :NOTE:
            # - position and pageNUM changes automatically represent
            #       the details of each job posting
            # :TODO:
            # - implement if elif statement for possible different websites
            search_url = "https://www.linkedin.com/jobs/search?" + \
                "keywords={}&location={}&distance=100&" + \
                "trk=public_jobs_jobs-search-bar_search-submit&" + \
                "position=1&pageNum=0"

        # Use urllib.parse to parse search terms and location
        #   (entities in the search term used for querying)
        # Encode non-alfanumeric characters to be compatible with URLs
        self.keywords_quoted = str(urllib.parse.quote(self.keywords, safe='')) 
        self.location_quoted = str(urllib.parse.quote(self.keywords, safe=''))
        self.url = search_url.format(
            self.keywords_quoted, self.location_quoted
            )

        logger.info("Generated Search URL = {}".format(self.url))

class JobDataScraper:

    def __init__(self,
                 job_searcher: JobSearcher, 
                 cli_args: argparse.ArgumentParser
                 ) -> None:
        self.job_searcher = job_searcher
        self.cli_args = cli_args
        self.chrome_driver = None
        self.__joblist = list()


    def _invoke_webdriver(self) -> webdriver.Chrome:

        url = self.job_searcher.url
        
        # Set configurations for the webdriver and invoke it
        chrome_options = Options()
        if self.cli_args.incognito:  # Run in incognito window
            chrome_options.add_argument("--incognito")  
        if self.cli_args.headless:  # Run chrome without UI
            chrome_options.add_argument("--headless")  
        chrome_driver = webdriver.Chrome(options=chrome_options)
        chrome_driver.maximize_window()
        logger.debug("search_url='{}'".format(url))
        chrome_driver.get(url)
        time.sleep(1)  # Sleep for 1 second to allow to 
        self.chrome_driver = chrome_driver
        # :REVIEW: 
        return chrome_driver

    def _scrape_webpage(self, source_code:str, html_tag_info:Sequence):

        # :REVIEW:
        soup = BeautifulSoup(source_code, 'html.parser')
        soup_search_results: bs4.element.ResultSet
        soup_search_results = soup.find_all(
            html_tag_info[0],
            attrs=html_tag_info[1]
        )
        
        return soup_search_results

    def __obtain_linkedin_joblist(self, min_post=1000):

        # :param min_post: Number of scraped job postings considered enough
        #     to conclude scraping for job postings

        chrome_driver = self.chrome_driver
        html_tags = self.get_linkedin_tags()
        cached_page_source = chrome_driver.page_source

        # Start scraping job posting information
        search_completed = False
        while not search_completed:

            htmlelement = chrome_driver.find_element_by_tag_name('html')
            htmlelement.send_keys(Keys.END)

            try:  # Identify 'See more jobs' botton and click on it
                chrome_driver.find_element_by_xpath(
                    '//button[text()="See more jobs"]').click()
            except Exception:
                logger.warning(
                    "Couldn't click on 'See more jobs' botton with webdriver"
                )
                time.sleep(1) # Wait for new jobs to load onto website
                continue

            soup_search_results = self._scrape_webpage(
                source_code=chrome_driver.page_source,
                html_tag_info=html_tags["job_posting"]
            )
            num_scraped_tags = len(soup_search_results) 

            if num_scraped_tags >= min_post:
                # If there are sufficiently many job postings scraped
                search_completed = True
                break
            elif num_scraped_tags == 0:
                # If there are no html tags found that match the 
                # specified template, conclude that 
                # something wrong happened: 
                # like an authentication wall getting raised 
                # or a CAPTCHA, or a connection error.

                soup_search_results = self._scrape_webpage(
                    source_code=cached_page_source,
                    html_tag_info=html_tags["job_posting"]
                )
                # :REVIEW: Maybe raise an error for specific user config
                break
            else:
                continue

        for ind, element in enumerate(soup_search_results):
            # :TODO:
            pass
            
            

    def _backup_joblist(self, filepath):
        # Backup the 
        with open(filepath, 'ab') as file_: #:FIXME:
            w = csv.writer(file_, dialect='excel') #:DEBUG:
            # w.writerows()

    @classmethod
    def get_linkedin_tags(cls):
        # :FIXME:
        # Hard-coded tags for current version of certain interface of
        #   websites, requires maintenance for long-term use

        linkedin_tags = {
            # Define which tags define the labelled information.

            # Tags related to Job postings
            "job_posting": (  # The main tag for each job posting
                "div", {
                    "class": "base-card base-card--link" \
                             + " "
                             + "base-search-card"
                             + " "
                             + "base-search-card--link job-search-card"
                }
            ),

            "job_title": (
                "h3", {
                    "class": "base-search-card__title"
                }
            ),

            "job_url": (
                "a", {
                    "class": "base-card__full-link",
                    "data-tracking-control-name": \
                    "public_jobs_jserp-result_search-card"
                }
            ),

            "job_location": (
                "span", {
                    "class": "job-search-card__location"
                }
            ),

            "job_company": (
                "a", {
                    "class": "hidden-nested-link",
                    "data-tracking-control-name": \
                    "public_jobs_jserp-result_job-search-card-subtitle"
                }
            ),

            # Data displayed in the side-pane OR individual pages:
            "details": (
                "div", {
                    "class": "details-pane__content details-pane__content--show",
                }
            ),

            "description": (
                "div", {
                    "class": "description__text description__text--rich"
                }
            ),

            "job_id": (
                "code", {
                    "style": "",
                    "id": "jobId"
                }
            ),

            # This should be equal to :cls.linkedin_tags.["job_title"]:
            "job_name": (
                "h2", {
                    "class": "top-card-layout__title topcard__title"
                }
            ),

            # This should be equal to :cls.linkedin_tags.["job_url"]:
            "job_link": (
                "a", {
                    "class": "topcard__link"
                }
            ),
        }
        return linkedin_tags


    def execute(self):

        chrome_driver = self._invoke_webdriver()

        if self.job_searcher.website == 'linkedin':
            self.__obtain_linkedin_joblist()

        chrome_driver.quit()



#################################################################
def v1_invoke_webdriver(url, CLI_ARGS):

    # Set configurations for the webdriver
    chrome_options = Options()
    chrome_options.add_argument("--incognito")  # Run in incognito window
    if CLI_ARGS.headless:
        chrome_options.add_argument("--headless")  # Run chrome without UI
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    driver.get(url)
    # time.sleep(3)
    logger.debug("search_url='{}'".format(url))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    return soup

# http://www.learningaboutelectronics.com/Articles/How-to-scroll-to-the-top-or-bottom-of-a-web-page-selenium-Python.php#:~:text=So%20the%20selenium%20module%20in%20Python%20is%20a,the%20page%20or%20the%20parameter%2C%20Keys.HOME%2C%20to%20

def template(JobSearch):
    soup = JobSearch.soup

    # Find all tags that are songs, eliminate all playlists
    soup_search_results = soup.find_all(
        "div",
        attrs={
            "id": "dismissible",
            "class": "style-scope ytd-video-renderer"
        }
    )
    # Log-Debug each search result
    logger.debug("soup_search_results=...")
    for ind, result in enumerate(soup_search_results):
        logger.debug("\t# RESULT-{:04d}:\n'{}'".format(ind, str(result))
    

# :XXX: DEPRECATED to be used within a class as a method
def form_search_url(config):
    jobsearch=dict()
    jobsearch["keywords"]=config["keywords"]
    jobsearch["location"]=config["location"]

    search_url="https://www.linkedin.com/jobs/search?" + \
        "keywords={}&location={}&" + \
        "trk=public_jobs_jobs-search-bar_search-submit&" + \
        "position=1&pageNum=0"
        # :NOTE:
        # - position and pageNUM changes automatically represent
        #       the details of each job posting
        # :TODO:
        # - implement if elif statement for possible different websites
        # :FIXME:
        #  Search URL is hardcoded to be for LinkedIn, fix this
        #       to be conditional according to  config file

    # Use urllib.parse to parse search terms and location for
    #   LinkedIn Search
    # For each entity in the search term used for querying
    for key, value in jobsearch.items():
        # Encode non-alfanumeric characters to be compatible with URLs
        jobsearch[key]=str(urllib.parse.quote(value, safe='')).lower()

    search_url=search_url.format(
        jobsearch["keywords"], jobsearch["location"]
    )
    jobsearch["url"]=search_url
    logger.info("Generated Search URL = {}".format(search_url))

    return jobsearch
