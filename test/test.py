import ally

params = {
    'ALLY_CONSUMER_KEY': "vKg4Okk9MDJ8pogzMlahQS1NcVsIwfYSlu9l5887UIM6",
    'ALLY_CONSUMER_SECRET': "JeJJfagm8qfx1l03dGvRxa8bGunTGjpbIXJzipaF1m47",
    'ALLY_OAUTH_TOKEN': "GKHMOAuNkwgY7bY6bw76fsJT1DcROUid8DOxOuCp8401",
    'ALLY_OAUTH_SECRET': "mWd99AbXjpDMCT1UqecBcvKmpJNpOAfnVid5uDA1rt06",
    'ALLY_ACCOUNT_NBR': "3LB69169"
}
a = ally.Ally(params)
qt = a.timesales('TSLA', '2022-09-29', '2022-10-01', dataframe=False)
accts = a.get_accounts()

import requests
url="https://devapi.invest.ally.com/v1/accounts.xml"


# location given here
location = "delhi technological university"
  
# defining a params dict for the parameters to be sent to the API
PARAMS = {'address':location}
  
# sending get request and saving the response as response object
r = requests.get(url, params = PARAMS)
  
# extracting data in json format
data = r.json()

print()