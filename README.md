# Coppertone

_Proof-of-concept Twitter scraping daemon_

## Task requirements
My interpretation: Write a Python program that monitors a Twitter account.

- Twitter handle to be provided as a command line argument
- At startup, print the 5 most recent tweets
- Then every 10 minutes, check for and display any new tweets
- Do not use any APIs that require user authentication, or a Twitter developer account
- Do not use open source libraries such as Twint or Tweepy to perform the heavy lifting

Extension 1:
- Add an API which can be queried via `curl` to dump all tweets collected as JSON

Extension 2:
- Write a `Dockerfile` to encapsulate this program
- Dockerfile should expose the API and enable tweets to be seen via `stdout`

## Assumptions
**Twitter handle:** The requirements indicate it should be provided as a command line argument. I chose to interpret this as it being the _only_ command line argument. There is no support for flags or other arguments to modify the default behaviour of the program.

**Output format:** No output format was prescribed for the program. Given the first extension to the requirements involves the development of a JSON API, I chose to assume the output from the program is for human consumption only; this means that the output is more expressive than that of a program designed for pipeline consumption. 

## Code structure
* **`coppertone.TweetMonitor`:** This class is used to monitor a Twitter handle for new tweets, and write them to `stdout` (via a logger).
* **`coppertone.CoppertoneServer`:** This class manages the web API server exposed by the program. It depends on `TweetMonitor` to operate.
* **`main`:** This is the main entrypoint for the program; it instantiates the two classes above and sets them running.