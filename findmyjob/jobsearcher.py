"""
    [summary]

[extended_summary]

:TODO:
- [ ] Write Module Docstring
- [ ] Remove unused imports
- [ ] Use Logger for logging execution
- [ ] Check Style for compatibility with PEP 8, 257 and 484 
"""

import configparser
import urllib.parse
import logging
from pprint import pprint  # Pretty-printer for testing

logger = logging.getLogger(__name__)

class JobSearcher:
    #:TODO:
    # [ ] Implement __str__ or at least __repr__ dunder methods

    def __init__(self, settings: dict) -> None:
        self._settings = settings
        self.website = settings["website"].casefold()
        self.keywords = settings["keywords"].lower()
        self.keywords_quoted = ""
        self.location = settings["location"].casefold()
        self.location_quoted = ""
        self.url = ""

        self._form_search_url()

    def _form_search_url(self):

        if self.website == 'linkedin':
            # :FIXME:
            #  Search URL is hardcoded to be for LinkedIn, fix this
            #       to be conditional according to  config file
            # :TODO:
            # - implement if elif statement for possible different websites
            # :NOTE:
            # - position and pageNUM changes automatically represent
            #       the details of each job posting
            search_url = r"https://www.linkedin.com/jobs/search?" + \
                r"keywords={}&location={}&distance=25&" + \
                r"trk=public_jobs_jobs-search-bar_search-submit&" + \
                r"position=1&pageNum=0"

        # Use urllib.parse to parse search terms and location
        #   (entities in the search term used for querying)
        # Encode non-alfanumeric characters to be compatible with URLs
        self.keywords_quoted = str(urllib.parse.quote(self.keywords, safe='')) 
        self.location_quoted = str(urllib.parse.quote(self.location, safe=''))
        self.url = search_url.format(
            self.keywords_quoted, self.location_quoted
        )

        logger.info(f"Generated Search URL = {self.url}")
