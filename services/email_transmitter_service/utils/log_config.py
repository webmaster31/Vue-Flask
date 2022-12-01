import os
import sys
import logging
from logging import Logger, getLevelName

import rollbar


class LoggerWithThirdParty(Logger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rollbar_secret = os.getenv('ROLLBAR_ACCESS_TOKEN')
        environment = os.getenv('STAGE') or "dev"

        if self.rollbar_secret:
            try:  # we dont want the api to go down if rollbar goes down
                rollbar.init(self.rollbar_secret, environment)
            except:
                print("Unable to initialize rollbar")
                pass

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        try:
            fn, lno, func, sinfo = self.findCaller(stack_info)
        except ValueError:  # pragma: no cover
            fn, lno, func, sinfo = "(unknown file)", 0, "(unknown function)", None

        extra_data = {
            'file': fn,
            'line': lno,
            'module': func,
            'sinfo': sinfo
        }
        super()._log(level, msg, args, exc_info, extra, stack_info)

        if self.rollbar_secret:
            try:
                if level >= 30:    # on warning or error or critical
                    rollbar.report_message(msg, getLevelName(level).lower(), extra_data=extra_data)
            except:
                print("Unable to report message to rollbar")
                pass

    def log_uncaught_exception(self, isRaise=True, exc_info=None, **kwargs):
        if self.rollbar_secret:
            try:
                rollbar.report_exc_info(exc_info=exc_info, extra_data=kwargs)
                rollbar.wait()
            except:
                print("Unable to catch errors with rollbar")
                pass
        if isRaise:
            raise

    def log_exception(self, message, level='error', request=None, extra_data=None, payload_data=None):
        if self.rollbar_secret:
            try:
                rollbar.report_message(message, level=level, request=request, extra_data=extra_data, payload_data=payload_data)
            except:
                print("Unable to catch errors with rollbar")
                pass


"""
All SQS services should use this logging config.
Provides a single place where all log config/level/formatting is setup so that one
can see source file, line numbers, and any other desired log fields.
"""

logger = LoggerWithThirdParty('main')
for h in logger.handlers:
    logger.removeHandler(h)
h = logging.StreamHandler(sys.stdout)
# use whatever format you want here
FORMAT = '%(asctime)-15s %(process)d-%(thread)d %(name)s [%(filename)s:%(lineno)d] :%(levelname)8s: %(message)s'
h.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(h)
logger.setLevel(logging.DEBUG)
# Suppress the more verbose modules
logging.getLogger('__main__').setLevel(logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.WARN)
