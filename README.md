#sinaWeibo

Crawl Weibo user and their tweets, and store in Mysql.
**Maybe Sina has modified the dom setting or ajax of their website, so my code may not work. But it's still can be a helpful demo**

## Usage
* Build Mysql database and tables, execute sina_weibo.sql. Insert a line in table `user`, the id is short id (length=10) of Weibo. This is the root of breadth-first search.
* Fill your cookies in cookies.txt.
* Modify userCrawler.py, including Mysql config and MY_UID.
* Runing userCrawler.py for 3~4 times. Each time is one level deeper of breadth-first search.

The weiboCrawler.py can be used in almost the same way as userCrawler.py. It will crawl tweets of users in table `user`.

## Acknowledge
Based on work of https://github.com/chyanju/wCrawler, Thanks Yanju Chen.
