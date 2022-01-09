# Find My Future Job

A web scraping project (written in Python) to find job announcements on certain platforms, like LinkedIn, according to user specified keywords (as search query terms) as such:

- Discipline / studied field of expertise
- Industry
- Demanded skills

Can also be used to extract data related to the search, like:

- Most Requested skills in the job announcements that the user's search query
yields
- Most job announcements per region.

## Examples

This section lists some examples for possible uses of the *package*

### Example 1 - Searching for Aerospace Engineering Jobs

aerospace engineering
cfd
fem
aerodynamics
optimization | optimisation

### Example 2 - Searching for Data Scientist Jobs

programming
modelling
statistics
database
spreadsheet
visualization
business intelligence

### Example 3 - Searching for Most Requested Skills for ML Engineer

mlops
excel
aws
azure
sas
powerbi
tableau
excel
spreadsheet
sql
scala
jira
apache
spark
hadoop
r
python
javascript
mssql
postgresql
mysql
nosql
datastax
cassandra
mongodb
ETL
linux
devops
git
github

## Technical Aspects

### Developer Roadmap
For the *minimum viable product*:

- [ ] Decide on which job-searching website(s), this tool should be compatible with
  - [ ] Inspect such job web-pages' source codes and check whether the webpages are static or dynamic after the search query response is generated.

  - [ ] Accordingly, establish a web-scraping method, i.e. decide whether to use BeautifulSoup or Selenium with Webdriver to scrape data from the website, according to the static/dynamic behavior of the website.

  - [ ] Check if the job search can be accessed without any means of authentication. If not, create a burner account for testing purposes in the website.

  - [ ] Check if there are any designated API endpoints to obtain job search query results.
    - From a quick search, it seems like LinkedIn previously had such a functionality, but has been deliberately deprecated to avoid competition.

- [ ] Decide on how the user will be using the tool
  - Input:
    - Maybe with a configuration.ini file
    - Maybe with a JSON object
    - Will it be a tool to be executed from the command line?
  - Output:
    - [ ] Which details are to be recorded?
      - If used for job announcement matching, it should at least record ANNOUNCEMENT_ID, ANNOUNCEMENT_URL, SCORE-or-PRIORITY
      - If used for inspecting most demanded skills, it should at least record SKILL_IDENTIFIER-or-_NAME, NUMBER_OF_OCCURANCES-or-SCORE
    - [ ] Decide on the way(s) to record the results from scraping data from the web.
      - Possibly in a .csv file

- [ ]  Implement asynchronous calls to web-scraping functions
  - [ ] There might be CAPTCHA tests if server thinks a bot is executing repeated consecutive commands, therefore it may require some testing to find ideal timing for not overloading the interface.



### Developer Notes
:TODO: 


:REVIEW:
May require delving into fuzzy string searches,