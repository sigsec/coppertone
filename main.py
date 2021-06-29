# This is a sample Python script.
import logging
import sys

import coppertone

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",)
logger = logging.getLogger(__name__)

WEBAPI_ENABLED = True


#
#
#

def main():
    if len(sys.argv) < 2:
        logger.warning("No username provided!")
    if len(sys.argv) != 2:
        logger.info("This program must be run with exactly one argument - the twitter handle of the account to monitor.")
        return

    monitor = coppertone.TweetMonitor(sys.argv[1])
    webapi = coppertone.CoppertoneServer(monitor)

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
