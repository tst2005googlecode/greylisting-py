Python greylisting script, using a MySQL database.
The script has been made to work with Exim, but could be used by other MTAs, or adapted to use another database.

The script does SPF check on incoming mail, if enabled in configuration file. If the SPF test passes, it will skip the greylist (since a domain supporting SPF is most likely to succeed the greylisting test also.)

The script can also use whitelists, with the ability to whitelist single IP addresses, and subnets using CIDR.

Another script is provided (clear-greylist.py) to cleanup the database, and should be executed in a cron job.

For installation instructions, see this page : http://code.google.com/p/greylisting-py/wiki/InstallationInstructions

# Downloading #
You can download the latest revision using SVN.
```
svn checkout http://greylisting-py.googlecode.com/svn/trunk/ greylisting-py
```

# Changelog #
**SVN [revision 18](https://code.google.com/p/greylisting-py/source/detail?r=18)**
  * Fixed a infinite loop bug ocurring when network whitelist was used.

**Version 1.0.1** (2008-01-29)
  * Fixed a bug due to new configuration variables

**Version 1.0**
  * Initial version released