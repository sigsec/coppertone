import json
import logging
import re
import time
import urllib.parse
from datetime import datetime
from typing import Optional, Dict, Any

import requests

logger = logging.getLogger(__name__)


class TweetMonitor:
    def __init__(self, twitter_handle: str, poll_rate: int):
        self.twitter_handle = twitter_handle
        self.poll_rate = poll_rate
        self.start_dt: Optional[datetime] = None

    def run(self):
        logger.info("Program will monitor account '%s'" % self.twitter_handle)
        self.start_dt = datetime.utcnow()

        twisc = Twisc()

        user_id = twisc.get_user_id(self.twitter_handle)

        twisc.get_user_tweets(user_id)

        while True:
            time.sleep(0.1)

    def stop(self):
        pass


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
        result_text = result.text
        result_json = result.json()

        # discard trash
        entries = result_json['timeline']['instructions'][0]['addEntries']['entries']

