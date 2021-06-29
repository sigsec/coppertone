# This is a sample Python script.
import logging
import sys

import coppertone

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",)
logger = logging.getLogger(__name__)

MONITOR_POLL_RATE = 60*10
WEBAPI_ENABLED = True
WEBAPI_PORT = 8080


#
#
#

def main():
    if len(sys.argv) < 2:
        logger.warning("No handle provided!")
    if len(sys.argv) != 2:
        logger.info("This program must be run with exactly one argument - the twitter handle of the account to monitor.")
        return

    monitor = coppertone.TweetMonitor(sys.argv[1], MONITOR_POLL_RATE)
    webapi = coppertone.CoppertoneServer(WEBAPI_PORT, monitor)

    try:
        if WEBAPI_ENABLED:
            logger.info("Web API is enabled.")
            webapi.run()

        monitor.run()

    except KeyboardInterrupt:
        webapi.stop()
        monitor.stop()


if __name__ == '__main__':
    main()
