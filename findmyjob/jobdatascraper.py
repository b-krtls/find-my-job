"""
    [summary]

[extended_summary]

:TODO:
- [ ] Write Module Docstring
- [ ] Remove unused imports
- [ ] Use Logger for logging execution
- [ ] Check Style for compatibility with PEP 8, 257 and 484 
"""
import logging
import time  # Possibly unused
import argparse
import re
import csv
import bs4
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from pprint import pprint  # Pretty-printer for testing
from typing import Iterable, Sequence, Union

from findmyjob.jobsearcher import JobSearcher

logger = logging.getLogger(__name__)


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

    def _scrape_webpage(self, source_code: str, html_tag_info: Sequence):

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
                time.sleep(1)  # Wait for new jobs to load onto website
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
        with open(filepath, 'ab') as file_:  # :FIXME:
            w = csv.writer(file_, dialect='excel')  # :DEBUG:
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

    def run(self):

        chrome_driver = self._invoke_webdriver()

        if self.job_searcher.website == 'linkedin':
            self.__obtain_linkedin_joblist()

        chrome_driver.quit()
