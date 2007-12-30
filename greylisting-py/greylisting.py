#!/usr/bin/python
# encoding: utf-8

# GREYLISTING SCRIPT
# By: Jean-Pascal Houde <jp@l3i.ca>
# Inspired by the exim.pl script by Roman Festchook ( http://llab.zhitomir.net/?greylist )

# Parameters : 
# greylisting.py <local-part> <domain> <sender-address> <sender-host-address>

# Return values :
# 0 - Try again - greylisting in progress
# 1 - OK, deliver the email
# 2 - SPF OK, deliver the email (greylist bypassed)
# 3 - Error - An error was encountered while greylisting (you should accept the email, and log the problem if possible)
# 4 - excluded - No greylisting done
# 5 - whitelisted

from config import *

RESULT_GREYLIST_DEFER = 0 # Message greylisted, try again later
# You should accept the message for return values > 0
RESULT_GREYLIST_OK = 1 
RESULT_SPF_OK = 2
RESULT_GREYLIST_ERROR = 3 
RESULT_EXCLUDED = 4
RESULT_WHITELIST = 5

RESULT_TEXT = ['GREYLIST', 'OK', 'SPF_PASS', 'ERROR', 'EXCLUDED', 'WHITELIST']

def testSPF(helo, emailfrom, host):
    spfResult = spf.check(host, emailfrom, helo)
    
    if spfResult[0] == 'pass':
        # SPF OK, bypass greylist
        return True
    else:
        return False

# ** Import packages **
import MySQLdb as mysql
import sys

try:
    # try importing spf
    import spf
except ImportError:
    # spf not instelled correctly, don't use it
    USE_SPF = False

try:
    # try import ipv4
    from ipv4 import CIDR
    CIDR_LOADED = True
except ImportError:
    CIDR_LOADED = False
    
# default result
result = RESULT_GREYLIST_ERROR

# HANDLE ALL ERRORS!
    
# get command line params
try: localPart = sys.argv[1]
except: localPart = ''
try: domain = sys.argv[2]
except: domain = ''
try: senderAddr = sys.argv[3]
except: senderAddr = ''
try: senderHost = sys.argv[4]
except: senderHost = ''
try: helo = sys.argv[5]
except: helo = ''

emailto = "%s@%s" % (localPart, domain)
emailfrom = senderAddr
host = senderHost

# connect to DB
db = mysql.connect(DB_HOST, user=DB_USER, passwd=DB_PASSWD, db=DB_NAME)
cur = db.cursor()

# Check if greylisting is enabled for the mailbox or not
cur.execute("SELECT 1 FROM GREYLIST_ENABLE WHERE (username = %s OR username = %s) AND domain = %s", ('%', localPart, domain))
if (not localPart in EXCLUDE_MAILBOXES) and cur.fetchone():
    # OK, greylisting enabled!
    
    # Check whitelist
    cur.execute("SELECT 1 FROM HOST_WHITELIST WHERE %s = host", (host, ))
    whiteListRes = cur.fetchone()
    if not whiteListRes:
        # host whitelist did not match, check net whitelist
        cur.execute("SELECT net FROM NET_WHITELIST")
        netResult = False
        
        # check each net for matches
        net = cur.fetchone()
        while net:
            netResult = CIDR(host) in CIDR(net[0])
            if netResult:
                break
            net = cur.fetchone() #loop...
        # add result to initial whitelist result
        whiteListRes = netResult
        
    # now make decision
    if whiteListRes:
        result = RESULT_WHITELIST
    else:
        # Check SPF
        if USE_SPF and testSPF(helo, emailfrom, host):
            result = RESULT_SPF_OK
        else:
            # Check current record
            cur.execute("SELECT UNIX_TIMESTAMP(block_expires)-UNIX_TIMESTAMP() FROM GREYLIST WHERE rcpt_to=%s AND mail_from=%s AND relay_ip=%s", (emailto, emailfrom, host))
            
            statusArray = cur.fetchone()
            
            if not statusArray:
                # Not record found, insert one
                cur.execute("INSERT INTO GREYLIST VALUES (NULL, %s, %s, %s, DATE_ADD(NOW(), INTERVAL 15 MINUTE), DATE_ADD(NOW(), INTERVAL 36 DAY), 1, 0, 0, 'AUTO', NOW(), NULL)", (host, emailfrom, emailto))
                
                result = RESULT_GREYLIST_DEFER
            else:
                # Record found, examine results
                if int(statusArray[0]) > 0:
                    # Ooops, host retryed too soon, it seems. Block message again and log BLOCK.
                    cur.execute("UPDATE GREYLIST SET blocked_count=blocked_count+1 WHERE rcpt_to=%s AND mail_from=%s AND relay_ip=%s", (emailto, emailfrom, host))
                    
                    result = RESULT_GREYLIST_DEFER
                else:
                    # Ok, host is clear to send mail here. log PASS and update expire date (36 days from now)
                    cur.execute("UPDATE GREYLIST SET passed_count=passed_count+1,  record_expires=DATE_ADD(NOW(), INTERVAL 36 DAY) WHERE rcpt_to=%s AND mail_from=%s AND relay_ip=%s", (emailto, emailfrom, host))
                    
                    result = RESULT_GREYLIST_OK
else:
    # no greylisting
    result = RESULT_EXCLUDED
    
# log mail
cur.execute("INSERT INTO MAIL_LOG VALUES(NULL, NOW(), %s, %s, %s, %s)", (emailto, emailfrom, host, RESULT_TEXT[result]))
    
    
print "Return code : %s" % result

sys.exit(result)
