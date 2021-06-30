import json
import logging
import re
import time
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Iterable

import requests

logger = logging.getLogger(__name__)


class TweetMonitor:
    def __init__(self, twitter_handle: str, poll_rate: int):
        self.twitter_handle = twitter_handle
        self.start_dt: Optional[datetime] = None
        self.poll_rate = poll_rate
        self.last_wake: Optional[datetime] = None
        self.next_wake: Optional[datetime] = None

        self.twisc = Twisc()
        self.user_id: Optional[str] = None
        self.tweets: List[Dict[str, Any]] = []

    def run(self, num_initial_tweets: int = 5):
        logger.info("Program will monitor handle '%s'" % self.twitter_handle)
        self.start_dt = datetime.utcnow()

        # Cache the user ID
        self.user_id = self.twisc.get_user_id(self.twitter_handle)
        if self.user_id is None:
            logger.error("No user with handle '%s' could be found." % self.twitter_handle)
            return

        self._fetch_initial_tweets(num_initial_tweets)

        while True:
            self.next_wake = datetime.utcnow() + timedelta(seconds=self.poll_rate)
            time.sleep(self.poll_rate)
            self.last_wake = datetime.utcnow()

            self._fetch_subsequent_tweets()

    def stop(self):
        pass

    def _fetch_initial_tweets(self, num_initial_tweets: int):
        logger.debug("Fetching %d initial tweets..." % num_initial_tweets)
        tweets = self.twisc.get_user_tweets(self.user_id)
        tweets = tweets[-num_initial_tweets:]

        self._notify_user_of_tweets(tweets)

    def _fetch_subsequent_tweets(self):
        logger.debug("Waking and checking for new tweets ...")
        tweets = self.twisc.get_user_tweets(self.user_id)

        new_tweets = filter(
            lambda x: not any(x['id_str'] == y['id_str'] for y in self.tweets),
            tweets)

        self._notify_user_of_tweets(new_tweets)

    def _notify_user_of_tweets(self, tweets: Iterable[Dict[str, Any]]):
        for tweet in tweets:
            logger.info("Tweet at %s: %s" % (tweet['created_at'], tweet['full_text']))
            self.tweets.append(tweet)






#
#
#

HEADER_AUTHORIZATION = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
HEADER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.116 Safari/537.36"


def refresh_guest_token() -> str:
    """Refresh the guest token used for API calls."""

    request = requests.get("https://twitter.com")
    matches = re.search(r'\("gt=(\d+);', request.text)
    return matches.group(1)


class Twisc:
    def __init__(self):
        self._session = requests.Session()
        self._session.headers["User-Agent"] = HEADER_USER_AGENT
        self._session.headers["Authorization"] = HEADER_AUTHORIZATION

        self._update_guest_token()

    def _update_guest_token(self):
        self._session.headers["x-guest-token"] = refresh_guest_token()

    @staticmethod
    def _query_encode(variables: Dict[str, Any]) -> str:
        return urllib.parse.quote_plus(json.dumps(variables))

    def get_user_id(self, username: str) -> Optional[str]:
        base = "https://api.twitter.com/graphql/jMaTS-_Ea8vh9rpKggJbCQ/UserByScreenName?variables="
        variables = {
            'screen_name': username,
            'withHighlightedLabel': False,
        }

        result = self._session.get(base + self._query_encode(variables))
        result_json = result.json()

        if len(result_json['data']) == 0:
            # User not found.
            return None

        user_id: str = result_json['data']['user']['rest_id']
        return user_id

    def get_user_tweets(self, user_id: str):
        """Fetch tweets for the given user ID, and return them sorted oldest to newest."""
        base = f"https://api.twitter.com/2/timeline/profile/{user_id}.json"
        variables = {
            'include_profile_interstitial_type': '1',
            'include_blocking': '1',
            'include_blocked_by': '1',
            'include_followed_by': '1',
            'include_want_retweets': '1',
            'include_mute_edge': '1',
            'include_can_dm': '1',
            'include_can_media_tag': '1',
            'skip_status': '1',
            'cards_platform': 'Web - 12',
            'include_cards': '1',
            'include_ext_alt_text': 'true',
            'include_quote_count': 'true',
            'include_reply_count': '1',
            'tweet_mode': 'extended',
            'include_entities': 'true',
            'include_user_entities': 'true',
            'include_ext_media_color': 'true',
            'include_ext_media_availability': 'true',
            'send_error_codes': 'true',
            'simple_quoted_tweet': 'true',
            'include_tweet_replies': 'true',
            'count': 20,
            'ext': 'mediaStats%2ChighlightedLabel',
        }

        result = self._session.get(base, params=variables)
        result_json = result.json()

        all_tweets: List[Dict[str, Any]] = sorted(
            result_json['globalObjects']['tweets'].values(),
            key=lambda x: datetime.strptime(x['created_at'], '%a %b %d %H:%M:%S %z %Y'),
            )

        return all_tweets

