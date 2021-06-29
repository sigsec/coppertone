# This is a sample Python script.
import json
import re
import sys
import urllib.parse
from typing import Dict, Any

import requests

import logging

import coppertone

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",)
logger = logging.getLogger(__name__)

WEBAPI_ENABLED = True

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

    def get_user_id(self, username: str) -> str:
        base = "https://api.twitter.com/graphql/jMaTS-_Ea8vh9rpKggJbCQ/UserByScreenName?variables="
        variables = {
            'screen_name': username,
            'withHighlightedLabel': False,
        }

        result = self._session.get(base + self._query_encode(variables))
        result_json = result.json()

        return result_json['data']['user']['rest_id']

    def get_user_tweets_deprecated(self, user_id: str):
        base = "https://twitter.com/i/api/graphql/TcBvfe73eyQZSx3GW32RHQ/UserTweets?variables="
        variables = {
            "userId": user_id,
            "count": 20,
            "withHighlightedLabel": True,
            "withTweetQuoteCount": True,
            "includePromotedContent": False,
            "withTweetResult": True,
            "withReactions": False,
            "withSuperFollowsTweetFields": False,
            "withUserResults": False,
            "withVoice": False,
            "withNonLegacyCard": False,
            "withBirdwatchPivots": False
        }

        result = self._session.get(base + self._query_encode(variables))
        result_json = result.json()

        # discard trash
        result_json = result_json['data']['user']['result']['timeline']['timeline']

    def get_user_tweets(self, user_id: str):
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


#
#
#

def main():
    if len(sys.argv) < 2:
        logger.warning("No username provided!")
    if len(sys.argv) != 2:
        logger.info("This program must be run with exactly one argument - the twitter handle of the account to monitor.")
        return

    requested_username = sys.argv[1]

    monitor = coppertone.TweetMonitor(sys.argv[1])
    webapi = coppertone.CoppertoneServer(monitor)

    if WEBAPI_ENABLED:
        logger.info("Web API is enabled.")
        webapi.run()

    twisc = Twisc()

    user_id = twisc.get_user_id(requested_username)

    twisc.get_user_tweets(user_id)


if __name__ == '__main__':
    main()
