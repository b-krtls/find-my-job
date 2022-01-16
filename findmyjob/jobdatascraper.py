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
import json
import bs4
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Iterable, Sequence, Tuple, Union
from pprint import pprint  # Pretty-printer for testing

from findmyjob.jobsearcher import JobSearcher

logger = logging.getLogger(__name__)


class _JobDataScraper:

    def __init__(self,
                 job_searcher: JobSearcher,
                 cli_args: argparse.ArgumentParser,
                 min_post: int = 1000,
                 ) -> None:
        self.min_post = min_post
        self.job_searcher = job_searcher
        self.cli_args = cli_args
        self.chrome_driver = None
        self._joblist = list()
        self._jobdict = dict()

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

    def _resolve_joblist(self):

        self._jobdict = {
            d["jobId"]: d for d in self._joblist
        }
        logging.info("Job dictionary formed")
        return

    def _backup_joblist_csv(self, filepath):

        # Backup the job data
        with open(filepath, 'ab') as file_:  # :FIXME:
            w = csv.writer(file_, dialect='excel')  # :DEBUG:
            # w.writerows()

    def _dump_json_filelist(self, filepath):
    
        with open(filepath, "w", encoding='utf8') as out_file:
            json.dump(self._jobdict, out_file, indent=4, ensure_ascii=False)
        logging.info(f"Scraped files are dumped to filepath={filepath}")


class LinkedinScraper(_JobDataScraper):

    def __init__(self, 
                 job_searcher: JobSearcher, 
                 cli_args: argparse.ArgumentParser,
                 min_post: int = 200,
                 ) -> None:
        super().__init__(job_searcher, cli_args, min_post)

    @classmethod
    def get_linkedin_tags(cls):

        # :NOTE:
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
                    "class": "decorated-job-posting__details"
                }
            ),

            "description": (
                "div", {
                    "class": "show-more-less-html__markup " \
                             + "show-more-less-html__markup--clamp-after-5"
                }
            ),

            "job_criteria": (
                "span", {
                    "class": "description__job-criteria-text "
                             + "description__job-criteria-text--criteria"
                }
            ),
        }
        return linkedin_tags

    @staticmethod
    def get_url_details(url: str) -> dict:

        pattern_jobId = r"\-([0-9]+)\?"
        pattern_refId = r"(refId=)(.*?)\&"
        pattern_trackingId = r"(trackingId=)(.*?)\&"

        re_pattern = pattern_jobId \
            + pattern_refId \
            + pattern_trackingId
        dummy = re.search(re_pattern, str(url))
        re_match = list(dummy.groups())

        url_details = {
            "url_href": url,
            "jobId": re_match[0],
            "refId": re_match[2],
            "trackingId": re_match[4],
        }
        url_details.update(
            {
            "url_parsed": r"https://www.linkedin.com/jobs/view/{}".format(
                url_details["jobId"])
            }
        )

        return url_details

    def __obtain_joblist(self):
        # Scrape LinkedIn Website with Selenium & Webdriver 
        # to assign an attribute as a :list: of :dict:'job details' 
        # :param min_post: Number of scraped job postings
        #       considered enough to conclude scraping for job postings

        chrome_driver = self.chrome_driver
        html_tags = self.get_linkedin_tags()
        cached_page_source = chrome_driver.page_source

        # Start scraping job posting information
        logger.info("Start scraping public job posts on LinkedIn")
        search_completed = False
        count_try = 0
        while not search_completed:

            htmlelement = chrome_driver.find_element_by_tag_name('html')
            htmlelement.send_keys(Keys.END)

            try:  # Identify 'See more jobs' botton and click on it
                count_try += 1
                chrome_driver.find_element_by_xpath(
                    '//button[text()="See more jobs"]').click()
                logger.warning(
                    f"Try{count_try:02d}-"
                    + "Successfully clicked on 'See more jobs' "
                    + "botton with webdriver"
                )
            except Exception:
                logger.warning(
                    f"Try{count_try:02d}-"
                    +"Couldn't click on 'See more jobs' botton with webdriver"
                )
                time.sleep(1)  # Wait for new jobs to load onto website

            soup_search_results = self._scrape_webpage(
                source_code=chrome_driver.page_source,
                html_tag_info=html_tags["job_posting"]
            )
            num_scraped_tags = len(soup_search_results) # :REVIEW::DEBUG:

            logger.info(
                r"'bs4.BeautifulSoup(..., 'html.parser') returned "
                + f"{len(soup_search_results)} instance(s) of "
                + "job_details for search terms"
            )
            logger.info(
                f"Minimum desired number of posts: min_post={self.min_post}"
            )

            if num_scraped_tags >= self.min_post:
                # If there are sufficiently many job postings scraped
                search_completed = True
                logger.info("Finished scraping public job posts on LinkedIn")
                break
            elif num_scraped_tags == 0:
                # If there are no html tags found that match the
                # specified template, conclude that
                # something wrong happened:
                # like an authentication wall getting raised
                # or a CAPTCHA, or a connection error.
                # and use cached page source before the error occurs

                soup_search_results = self._scrape_webpage(
                    source_code=cached_page_source,
                    html_tag_info=html_tags["job_posting"]
                )
                logger.warning("Website blocked")
                break
            elif count_try > 9: # Hard-coded limit for try block
                break
            else:
                continue

        logger.info("Finished scraping public job posts on LinkedIn")

        logger.info("Start parsing and processing HTML elements")
        for ind, element in enumerate(soup_search_results):
            # For each job post :element:, extract
            #   :key:'url_href'
            #   :key:'jobId'
            #   :key:'refId'
            #   :key:'trackingId'
            #   :key:'title'
            #   :key:'location'
            #   :key:'company'
            #   into a :dict:'job_attributes'
            job_attributes = {}
            # :DEBUG: Does .find(..., attrs=...) work?
            # Job title
            tag_title = element.find(
                html_tags["job_title"][0],
                attrs=html_tags["job_title"][1]
                )
            title = tag_title.text

            # Job location
            tag_location = element.find(
                html_tags["job_location"][0],
                attrs=html_tags["job_location"][1]
                )
            location = tag_location.text

            # Company name
            tag_company = element.find(
                html_tags["job_company"][0],
                attrs=html_tags["job_company"][1]
                )
            company = tag_company.text
        
            # URL
            tag_url = element.find(
                html_tags["job_url"][0], 
                attrs=html_tags["job_url"][1]
                )
            url = tag_url["href"]
            url_details: dict = self.get_url_details(url)

            job_attributes.update(
                {
                    "title": re.sub('\s+', ' ', title).strip(' '),
                    "location": re.sub('\s+', ' ', location).strip(' '),
                    "company": re.sub('\s+', ' ', company).strip(' '),
                }
            )
            job_attributes.update(url_details)

            self._joblist.append(job_attributes)

        logger.info("Finished processing Job List")
    
    def __obtain_job_contents(self):

        pass #:FIXME:
        chrome_driver = self.chrome_driver
        html_tags = self.get_linkedin_tags()
        tag_4_details_listed = [
            html_tags["details"][0],
            *next(iter(html_tags["details"][1].items()))
        ]

        logger.info(
            "Start scraping job details and description for each job"
        )
        # For each job post, go to the job post webpage and scrape 
        #   job description and details

        for job_attributes in self._joblist:

            try:
                time.sleep(1)
                url_parsed = job_attributes["url_parsed"]
                chrome_driver.get(url_parsed)

                # If website loads an authentication wall
                if "authwall" in str(chrome_driver.current_url).lower():
                    logger.warning(
                        "Accessing job post with " \
                        + "jobId={}, ".format(job_attributes["jobId"]) \
                        + "(url_parsed={}) ".format(
                                job_attributes["url_parsed"]
                                ) \
                        + "was blocked with Authentication Wall "
                        + "and Job Details could not be read"
                        )
                    time.sleep(2.5) # Hard-sleep
                    continue
                # If website does not load an authentication wall
                # Wait a variable amount of time, maximum 10 seconds,
                #   to check if website has loaded a tag with the
                #   information defined in dict:'html_tags'["details"]
                element = WebDriverWait(chrome_driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, 
                         r"//{}[@{}='{}']".format(*tag_4_details_listed)
                        )
                    )
                )

                soup_search_results = self._scrape_webpage(
                    source_code=chrome_driver.page_source,
                    html_tag_info=html_tags["details"]
                )

                # Sanity Check :REVIEW::DEBUG:
                    # It should always return 1 item
                logger.info(
                    "For jobId={}, ".format(job_attributes["jobId"]) \
                    + "(url_parsed={}) ".format(
                            job_attributes["url_parsed"]
                            )
                    + r"'bs4.BeautifulSoup(..., 'html.parser') returned "\
                    + f"{len(soup_search_results)} instance(s) of " \
                    + "job_details"
                    )
                assert len(soup_search_results) == 1
                element = soup_search_results[0]

                tag_job_description = element.find(
                    html_tags["description"][0],
                    attrs=html_tags["description"][1]
                    )
                job_description = tag_job_description.text 
                # :TODO: remove <br> and other style tags from job_description
                job_attributes.update(
                    {"job_description": \
                        re.sub('\s+', ' ', job_description).strip(' ')}
                )

            except Exception as raised_error:
                logging.exception("\n"+str(raised_error)+"\n")
                continue
            
            finally:
                try:
                    
                    tag_job_criteria = element.find_all(
                        html_tags["job_criteria"][0],
                        attrs=html_tags["job_criteria"][1]
                        )
                    # :X:
                    # print(*[i.text for i in tag_job_criteria])
                    # print(job_attributes["title"])

                    # :TODO:
                    # Interpret which values are provided in website
                    # with additional HTML parsing
                    seniority_level = tag_job_criteria[0].text
                    employment_type = tag_job_criteria[1].text
                    job_function = tag_job_criteria[2].text
                    industries = tag_job_criteria[3].text

                    job_attributes.update(
                        {
                            "seniority_level": \
                                re.sub('\s+',' ',seniority_level).strip(' '),
                            "employment_type": \
                                re.sub('\s+',' ',employment_type).strip(' '),
                            "job_function": \
                                re.sub('\s+',' ',job_function).strip(' '),
                            "industries": \
                                re.sub('\s+',' ',industries).strip(' ')
                        }
                    )
                except Exception:
                    logging.warning(
                        "For jobId={}, ".format(job_attributes["jobId"])
                        + "(url_parsed={}) ".format(
                            job_attributes["url_parsed"]
                            )
                        + "Not All job criteria is not supplied, "
                        + "hence they will not be stored."
                    )


    def run(self):

        chrome_driver = self._invoke_webdriver()
        self.__obtain_joblist()
        self.__obtain_job_contents()
        self._resolve_joblist()


    def backup(self, filepath):

        # :TODO: Implement multiple ways to backup the scraped data
        self._dump_json_filelist(filepath)

    def quit(self):

        self.chrome_driver.quit()
