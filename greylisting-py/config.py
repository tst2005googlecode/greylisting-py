# encoding: utf-8

# This file contains configuration information for the greylisting.py script.
# You need to set DB parameters here before running the script.

# MySQL connection parameters
DB_HOST = "localhost"
DB_NAME = "greylist"
DB_USER = "exim"
DB_PASSWD = ""

# If True, greylisting will be bypassed if sender passes SPF test
USE_SPF = True

# Always exclude these mailbox names
EXCLUDE_MAILBOXES = ('abuse', 'postmaster', )

# Cleanup configuration
BLOCK_REMOVE_DELAY = 8 # delete record x hours after block_expires time
MAIL_LOG_REMOVE_DELAY = 7 # delete mail logs after x days

