sinaWeibo
=========

<p style="color:red;">Maybe Sina has modified the dom setting or ajax of their website, so my code may not work. But it's a demo that may help you.</p>

Base on work of https://github.com/chyanju/wCrawler
Crawl user and Weibo, and store in Mysql.

1. Mysql, execute sina_weibo.sql. Add a seed in table user, id(the short id, size is 10) at least.
2. Fill your cookies in cookies.txt
3. Update userCrawler.py, including Mysql config and MY_UID.
4. Runing it 3~4 times. It may takes a few hours, so I do not add a 'For'.

* The weiboCrawler.py can be used in almost the same way as userCrawler.py.
