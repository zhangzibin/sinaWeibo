#sinaWeibo

Crawl Weibo user and their tweets, and store in Mysql.

**Maybe Sina has modified the dom setting or ajax of their website, so my code may not work. But it's still can be a helpful demo**

## Usage
1. Build Mysql database and tables, execute sina_weibo.sql. Insert a line in table `user`, the id is short id of Weibo, size is 10. This is the root of breadth-first search.
2. Fill your cookies in cookies.txt
3. Modify userCrawler.py, including Mysql config and MY_UID.
4. Runing userCrawler.py for 3~4 times. Each time is one level deeper of breadth-first search.

* The weiboCrawler.py can be used in almost the same way as userCrawler.py. It will crawl tweets of users in table `user`.

## Acknowledge
Based on work of https://github.com/chyanju/wCrawler, Thanks Yanju Chen.
