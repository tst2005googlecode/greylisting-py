# encoding: utf-8

# This file contains configuration information for the greylisting.py script.
# You need to set DB parameters here before running the script.

# MySQL connection parameters
DB_HOST = "localhost"
DB_NAME = "exim_greylist"
DB_USER = "exim"
DB_PASSWD = ""

# If True, greylisting will be bypassed if sender passes SPF test
USE_SPF = True

# Always exclude these mailbox names
EXCLUDE_MAILBOXES = ['abuse', 'postmaster']

