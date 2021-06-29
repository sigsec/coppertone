# This is a sample Python script.
import json
import re
import urllib.parse
from typing import Dict, Any

import requests


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
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





def build_headers() -> Dict[str, str]:
    # noinspection PyDictCreation
    r_headers: Dict[str] = {}

    r_headers["authority"] = "twitter.com"
    r_headers["pragma"] = "no-cache"
    r_headers["accept"] = "*/*"
    r_headers["Content-Type"] = "application/json"
    r_headers["sec-fetch-site"] = "same-origin"
    r_headers["sec-fetch-mode"] = "cors"
    r_headers["sec-fetch-dest"] = "empty"
    r_headers["accept-language"] = "en-GB,en;q=0.9"
    r_headers["cache-control"] = "no-cache"
    r_headers["x-twitter-client-language"] = "en-GB"
    r_headers["x-twitter-active-user"] = "yes"
    r_headers["authorization"] = HEADER_AUTHORIZATION
    r_headers["x-csrf-token"] = "427effda2d5ef6e0d5a0008b347e92bc"
    r_headers["x-guest-token"] = refresh_guest_token()
    r_headers["user-agent"] = HEADER_USER_AGENT
    r_headers["referer"] = "https://twitter.com/sample"

    return r_headers


def build_query_url() -> str:
    base = "https://twitter.com/i/api/graphql/TcBvfe73eyQZSx3GW32RHQ/UserTweets?variables="
    variables = {
        "userId": "751173",
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

    return base + urllib.parse.quote_plus(json.dumps(variables))


def do_request():
    url = build_query_url()
    r_headers = build_headers()

    raw_result = requests.get(url, headers=r_headers)
    result_text = raw_result.text
    result = raw_result.json()

    # discard trash
    result = result['data']['user']['result']['timeline']['timeline']

    print(raw_result)


def main():
    # Use a breakpoint in the code line below to debug your script.
    twisc = Twisc()

    user_id = twisc.get_user_id('TwitterDev')

    twisc.get_user_tweets(user_id)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
