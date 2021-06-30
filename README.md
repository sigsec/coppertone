# Coppertone

> _Proof-of-concept Twitter scraping daemon_

## Task requirements
_These are not the verbatim requirements provided from the upstream source. They have been rewritten to avoid finger-printing, based on the request from the originator. It was trivial to locate several other (attempted) implementations of the original specification._

My interpretation: **Using Python, write a program that watches a Twitter handle.**

- Twitter handle to be provided as a command line argument
- At startup, print the 5 most recent tweets
- Then every 10 minutes, check for and display any new tweets
- Do not use APIs that require user authentication
- Do not use open source libraries such as Twint to perform the core logic

Extension 1:
- Add an API which can be queried via `curl` to dump all tweets collected as JSON

Extension 2:
- Write a `Dockerfile` to encapsulate this program
- Dockerfile should expose the API and enable tweets to be seen via `stdout`



## Assumptions and interpretations
**Twitter handle:** The requirements indicate it should be provided as a command line argument. I chose to interpret this as it being the _only_ command line argument. There is no support for flags or other arguments to modify the default behaviour of the program.

**Output format:** No output format was prescribed for the program. Given the first extension to the requirements involves the development of a JSON API, I chose to assume the output from the program is for human consumption only; this means that the output is more expressive than that of a program designed for pipeline consumption. 

**Process exit status:** There were no stipulations about the process exit status in the specification. Consequently, the process always exits with zero.

**Data model:** There were no stipulations about the data model to use. Consequently, the tweet objects returned by the Coppertone API are the same as those received from the upstream Twitter API, without modification or normalisation.

**Error handling:** There were no stipulations about error handling. Consequently, only minimal error handling has been added covering exclusively the most common issues (no handle provided, handle does not exist, token has expired).



## Sample output
Output from the program while monitoring the `Every3Minutes` handle, chosen for its frequent and predictable tweet timings.

```text
19:49:20 INFO [__main__]  Web API is enabled.
19:49:20 INFO [coppertone.TweetMonitor]  Program will monitor handle 'Every3Minutes'
19:49:21 DEBUG [coppertone.TweetMonitor]  Fetching 5 initial tweets...
19:49:21 DEBUG [coppertone.TweetMonitor]  Found 5 new tweets
19:49:21 INFO [coppertone.TweetMonitor]  Tweet at Wed Jun 30 09:36:03 +0000 2021: In the antebellum American South--a white slaver just traded a person. https://t.co/vCbBhCs2Bt
19:49:21 INFO [coppertone.TweetMonitor]  Tweet at Wed Jun 30 09:39:02 +0000 2021: In the antebellum U.S. South---an enslaved person's friend was just sold.
19:49:21 INFO [coppertone.TweetMonitor]  Tweet at Wed Jun 30 09:42:03 +0000 2021: In the antebellum United States--someone just bought someone's grandparent.
19:49:21 INFO [coppertone.TweetMonitor]  Tweet at Wed Jun 30 09:45:02 +0000 2021: In the antebellum United States, a slaver just bought a slave.
19:49:21 INFO [coppertone.TweetMonitor]  Tweet at Wed Jun 30 09:48:02 +0000 2021: In the antebellum United States---a white slaver just bought a black person's grandchild. https://t.co/rh3nHvjB5A
19:59:21 DEBUG [coppertone.TweetMonitor]  Waking and checking for new tweets ...
19:59:23 DEBUG [coppertone.TweetMonitor]  Found 3 new tweets
19:59:23 INFO [coppertone.TweetMonitor]  Tweet at Wed Jun 30 09:51:02 +0000 2021: In the antebellum United States---a white person just purchased a human being's friend.
19:59:23 INFO [coppertone.TweetMonitor]  Tweet at Wed Jun 30 09:54:02 +0000 2021: In the antebellum U.S.--a white slaver just sold an enslaved person's friend.
19:59:23 INFO [coppertone.TweetMonitor]  Tweet at Wed Jun 30 09:57:02 +0000 2021: In the antebellum U.S. South someone was just purchased.
```



## Operation
### Direct execution
Before the script will operate, there are certain Python package dependency requirements that need to be met. Install these using `pip install -r requirements.txt` (or as appropriate for your system).

Execute `main.py` using Python, and pass in the account to monitor. The exact command used will vary depending on your system configuration, but may look like:

```shell
# To display the "no handle provided" error, run without arguments:
python3 main.py

# For routine operation, provide the handle. e.g. TwitterDev:
python3 main.py TwitterDev
```

### Using Docker
A Dockerfile is provided so that the application can be effectively daemonised. The specific instructions you should follow will vary depending on your desired configuration. A sample sequence of commands is shown:

```shell
# Build the docker image
docker build -t coppertone .

# Execute the docker image, making sure to bind the API port
docker run --rm -it -p 8080:8080 coppertone TwitterDev
```

### Querying the API
The program includes a basic API, which can be used to programmatically query the state of the process. By default, this listens on port `8080` of all local interfaces. For end-user customisation, specify an alternate port binding using the Docker instructions above.

There are two supported API endpoints:

- `GET /tweets`: This returns the list of all accumulated tweets for the given handle, returned as a JSON array.
- `GET /`: This is an alias for `GET /tweets`.
- `GET /status`: This displays some statistical information about the server and its status.

For example:

```shell
# To query the status endpoint:
$ curl "http://localhost:8080/status"
{"coppertone": {"server_started": "2021-06-30 09:49:20.179096", "requests_handled": 11}, "monitor": {"twitter_handle": "Every3Minutes", "user_id": "2899773086", "num_tweets_cached": 8, "poll_rate": 600, "last_wake": "2021-06-30 09:59:21.945702", "next_wake": "2021-06-30 10:09:23.146183"}}

# To fetch the list of tweets (truncated for length)
$ curl "http://localhost:8080/"
[{"created_at": "Wed Jun 30 09:57:02 +0000 2021", "id_str": "1410175538698895376", "full_text": "In the antebellum U.S. South someone was just purchased.", "display_text_range": [0, 56], "entities": {}, "source": "<a href=\"http://wcm1.web.rice.edu\" rel=\"nofollow\">E3MBot</a>", "user_id_str": "2899773086", "retweet_count": 1, "favorite_count": 0, "reply_count": 0, "quote_count": 0, "conversation_id_str": "1410175538698895376", "lang": "en"}, ...]
```



## Code structure
* **`coppertone.TweetMonitor`:** This class is used to monitor a Twitter handle for new tweets, and write them to `stdout` (via a logger).
* **`coppertone.CoppertoneServer`:** This class manages the web API server exposed by the program. It depends on `TweetMonitor` to operate.
* **`main`:** This is the main entrypoint for the program; it instantiates the two classes above and sets them running.
