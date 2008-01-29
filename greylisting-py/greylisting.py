#!/usr/bin/python
# encoding: utf-8

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# *****************************************************************************************
# GREYLISTING SCRIPT
# By: Jean-Pascal Houde <jp@l3i.ca>
# Inspired by the exim.pl script by Roman Festchook ( http://llab.zhitomir.net/?greylist )
# *****************************************************************************************
# Parameters : 
# greylisting.py <local-part> <domain> <sender-address> <sender-host-address> <helo-name>
# 
# Return values : greylist, ok, spfok, excluded, whitelisted
# greylist should trigger a 4xx temporary error, you should accept the message for any other
# return value.
# Return code is always 0, unless an exception occurs.
# *****************************************************************************************

from config import *
import MySQLdb as mysql
import sys
try:
    import spf
except ImportError:
    # spf not instelled correctly, don't use it
    USE_SPF = False
try:
    from ipv4 import CIDR
    CIDR_LOADED = True
except ImportError:
    CIDR_LOADED = False

# connect to DB
db = mysql.connect(DB_HOST, user=DB_USER, passwd=DB_PASSWD, db=DB_NAME)
cur = db.cursor()

############################ functions ############################

def testSPF(helo, mailFrom, hostAddr):
    spfResult = spf.check(hostAddr, mailFrom, helo)
    
    if spfResult[0] == 'pass':
        # SPF OK, bypass greylist
        return True
    else:
        return False

def checkEnabled(lp, domain):
    """check if a given address (local part, domain) should be checked for greylisting. Greylisting has to be enabled in the
       GREYLIST_ENABLE table for each address or domain"""
    cur.execute("SELECT 1 FROM GREYLIST_ENABLE WHERE (username = %s OR username = %s) AND domain = %s", ('*', lp, domain))
    
    return (lp not in EXCLUDE_MAILBOXES) and cur.fetchone()

def checkWhitelisted(hostAddr):
    """check if an hostAddr/net is whitelisted"""

    # check hostAddr
    cur.execute("SELECT 1 FROM HOST_WHITELIST WHERE %s = host", (hostAddr, ))
    res = cur.fetchone()
    if res:
        return True

    # check net
    if CIDR_LOADED:
        cur.execute("SELECT net FROM NET_WHITELIST")
        net = cur.fetchone()
        while net:
            if CIDR(hostAddr) in CIDR(net[0]):
                # network matches whitelist
                return True

    return False
    
 

def greylist(localPart, domain, mailFrom, hostAddr, helo):
    """runs greylisting process and returns the result"""
    emailto = "%s@%s" % (localPart, domain)

    # Check if greylisting is enabled for the mailbox or not
    if not checkEnabled(localPart, domain):
        return 'excluded'
        
    # Check whitelist
    whiteListRes = checkWhitelisted(hostAddr)
    if whiteListRes:
        return 'whitelisted'
        
    # Check SPF
    if USE_SPF and testSPF(helo, mailFrom, hostAddr):
        return 'spfok'

    # Check current record
    cur.execute("SELECT UNIX_TIMESTAMP(block_expires)-UNIX_TIMESTAMP() \
                        FROM GREYLIST WHERE rcpt_to=%s AND \
                        mail_from=%s AND relay_ip=%s", (emailto, mailFrom, hostAddr))
    statusArray = cur.fetchone()

    if not statusArray:
        # Not record found, insert one
        cur.execute("INSERT INTO GREYLIST VALUES (NULL, %s, %s, %s, \
                                                  DATE_ADD(NOW(), INTERVAL " + str(INITIAL_BLOCK) +" MINUTE), \
                                                  DATE_ADD(NOW(), INTERVAL " + str(EXPIRE_DELAY) + " DAY), 1, 0, 0, \
                                                  'AUTO', NOW(), NULL)", (hostAddr, mailFrom, emailto))
        return 'greylist'
        
    if int(statusArray[0]) > 0:
        # Ooops, host retryed too soon, it seems. Block message again and log BLOCK.
        cur.execute("UPDATE GREYLIST SET blocked_count=blocked_count + 1 \
                            WHERE rcpt_to=%s AND mail_from=%s AND relay_ip=%s", (emailto, mailFrom, hostAddr))
        
        return 'greylist'
    else:
        # Ok, host is clear to send mail here. log PASS and update expire date (36 days from now)
        cur.execute("UPDATE GREYLIST SET passed_count=passed_count+1, \
                                         record_expires=DATE_ADD(NOW(), INTERVAL 36 DAY) \
                            WHERE rcpt_to=%s AND mail_from=%s AND relay_ip=%s", (emailto, mailFrom, hostAddr))
        
        return 'ok'

# main program starts here

# get command line params
args = sys.argv[1:6]

if len(args) != 5:
    print "This commands takes 5 parameters : "
    print "greylisting.py <local-part> <domain> <sender-address> <sender-host-address> <helo-name>"
    sys.exit(1)

value = greylist(*args)

# log mail
cur.execute("INSERT INTO MAIL_LOG VALUES(NULL, NOW(), %s, %s, %s, %s)", ('%s@%s' % (args[0], args[1]), args[2], args[3], value))

sys.stdout.write(value)
sys.exit(0)
