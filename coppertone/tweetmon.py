import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class TweetMonitor:
    def __init__(self, twitter_username: str):
        self.twitter_username = twitter_username
        self.start_dt: Optional[datetime] = None

    def start(self):
        logger.info("Program will monitor account '%s'" % self.twitter_username)
        self.start_dt = datetime.utcnow()
