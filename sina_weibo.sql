CREATE DATABASE /*!32312 IF NOT EXISTS*/`sina_weibo` /*!40100 DEFAULT CHARACTER SET utf8 */;

use `sina_weibo`;

CREATE TABLE `user` (
  `id` bigint NOT NULL,
  `accountID` varchar(16) DEFAULT NULL,
  `nickName` varchar(64) NOT NULL,
  `isFetched` tinyint(1) NOT NULL DEFAULT '0',
  `sex` char(1) NOT NULL,
  PRIMARY KEY (`id`,`accountID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `relation` (
	`id` bigint NOT NULL AUTO_INCREMENT,
	`curUser` bigint NOT NULL,
	`follower` bigint NOT NULL,
	PRIMARY KEY (`id`),
	FOREIGN KEY (`curUser`) REFERENCES `user`(`id`) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (`follower`) REFERENCES `user`(`id`) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `weibo` (
	`weiboID` varchar(16) NOT NULL,
	`uid` bigint NOT NULL,
	`content` varchar(1024) NOT NULL,
	`pubTime` datetime NOT NULL,
	PRIMARY KEY (`weiboID`),
	FOREIGN KEY (`uid`) REFERENCES `user`(`id`) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

insert into user values(2452319582, '1005052452319582', 'CH≈¨¡¶’“∑ΩœÚ', 0, 'f'); 
