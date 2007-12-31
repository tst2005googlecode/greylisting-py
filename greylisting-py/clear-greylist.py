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
# GREYLISTING *cleanup* SCRIPT
# By: Jean-Pascal Houde <jp@l3i.ca>
# *****************************************************************************************

import MySQLdb as mysql
import sys
from config import *

# connect to DB
db = mysql.connect(DB_HOST, user=DB_USER, passwd=DB_PASSWD, db=DB_NAME)
cur = db.cursor()
innerCur = db.cursor()

# Check if greylisting is enabled for the mailbox or not
cur.execute("SELECT id, relay_ip, mail_from, rcpt_to, blocked_count, passed_count \
             FROM GREYLIST \
             WHERE (passed_count=0 and (UNIX_TIMESTAMP() - UNIX_TIMESTAMP(block_expires)) > " + str(BLOCK_REMOVE_DELAY * 3600) + ") \
             OR (UNIX_TIMESTAMP() - UNIX_TIMESTAMP(record_expires) > 0) ", ())
row = cur.fetchone()
while row:
    
    host = row[1]
    mailfrom = row[2]
    rcptto = row[3]
    recordId = row[0]
    blockcount = str(int(row[4]))
    passcount = str(int(row[5]))
    
    if passcount == "0":
        # log BLOCKED attempts
        innerCur.execute("INSERT INTO SPAM_LOG VALUES (NULL, %s, %s, %s, " + blockcount + ", " + passcount + ", NOW())", (host, mailfrom, rcptto))
        #print "Spam!"
    
    innerCur.execute("DELETE FROM GREYLIST WHERE id = " + str(recordId), ())
    #print "Deleted line %s : %s, %s, %s" % (recordId, mailfrom, rcptto, host)
    
    # fetch another row
    row = cur.fetchone()

# clear old entries from mail log
cur.execute("DELETE FROM MAIL_LOG WHERE DATE_ADD(date, INTERVAL " + str(MAIL_LOG_REMOVE_DELAY) + " DAY) < NOW()")

# optimize tables
cur.execute("OPTIMIZE TABLE GREYLIST", ())
cur.execute("OPTIMIZE TABLE MAIL_LOG", ())
cur.execute("OPTIMIZE TABLE SPAM_LOG", ())
cur.execute("OPTIMIZE TABLE HOST_WHITELIST", ())
cur.execute("OPTIMIZE TABLE NET_WHITELIST", ())
cur.execute("OPTIMIZE TABLE GREYLIST_ENABLE", ())
