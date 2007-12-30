
--
-- Structure de la table `GREYLIST`
--

CREATE TABLE IF NOT EXISTS `GREYLIST` (
  `id` bigint(20) unsigned NOT NULL auto_increment,
  `relay_ip` varchar(16) default NULL,
  `mail_from` varchar(255) default NULL,
  `rcpt_to` varchar(255) default NULL,
  `block_expires` datetime NOT NULL default '0000-00-00 00:00:00',
  `record_expires` datetime NOT NULL default '0000-00-00 00:00:00',
  `blocked_count` bigint(20) NOT NULL default '0',
  `passed_count` bigint(20) NOT NULL default '0',
  `aborted_count` bigint(20) NOT NULL default '0',
  `origin_type` enum('MANUAL','AUTO') NOT NULL default 'MANUAL',
  `create_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `last_update` timestamp NULL default NULL,
  PRIMARY KEY  (`id`),
  KEY `triplet_INDEX` (`relay_ip`,`mail_from`,`rcpt_to`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=170700 ;

-- --------------------------------------------------------

--
-- Structure de la table `GREYLIST_ENABLE`
--

CREATE TABLE IF NOT EXISTS `GREYLIST_ENABLE` (
  `username` varchar(255) NOT NULL default '',
  `domain` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`username`,`domain`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `HOST_WHITELIST`
--

CREATE TABLE IF NOT EXISTS `HOST_WHITELIST` (
  `host` varchar(16) NOT NULL default '',
  `commentaire` text NOT NULL,
  PRIMARY KEY  (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `MAIL_LOG`
--

CREATE TABLE IF NOT EXISTS `MAIL_LOG` (
  `id` bigint(20) NOT NULL auto_increment,
  `date` datetime NOT NULL default '0000-00-00 00:00:00',
  `mailto` varchar(255) NOT NULL default '',
  `mailfrom` varchar(255) NOT NULL default '',
  `host` varchar(255) NOT NULL default '',
  `result` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1311220 ;

-- --------------------------------------------------------

--
-- Structure de la table `NET_WHITELIST`
--

CREATE TABLE IF NOT EXISTS `NET_WHITELIST` (
  `net` varchar(19) NOT NULL default '',
  `commentaire` text NOT NULL,
  PRIMARY KEY  (`net`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `SPAM_LOG`
--

CREATE TABLE IF NOT EXISTS `SPAM_LOG` (
  `id` bigint(20) unsigned NOT NULL auto_increment,
  `relay_ip` varchar(16) NOT NULL default '',
  `mail_from` varchar(255) NOT NULL default '',
  `rcpt_to` varchar(255) NOT NULL default '',
  `blocked_count` bigint(20) NOT NULL default '0',
  `passed_count` bigint(20) NOT NULL default '0',
  `last_update` datetime NOT NULL default '0000-00-00 00:00:00',
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=163982 ;

