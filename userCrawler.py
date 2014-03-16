import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import urllib2
import time
from bs4 import BeautifulSoup
import MySQLdb

#connect db
db = MySQLdb.connect(host="localhost", user="USER", passwd="PSW", db="sina_weibo")
cursor = db.cursor()

#config
CRAWL_DEPTH = 3
FP_COOKIE = open("cookies.txt","r")
ARGS_COOKIE = FP_COOKIE.readline()
FP_COOKIE.close()
MY_UID = "YOUR ID";

#class: User
class User:
    def __init__(self):
        self.id = 0
        self.accountID = ''
        self.nickName = ''
        self.sex = ''

#fetch html
def fetchUrl(url):
    request = urllib2.Request(url);
    request.add_header('Cookie',ARGS_COOKIE)
    response = urllib2.urlopen(request)
    return response.read()

#get page num
def getPageNum(html):
    start = html.find('W_pages') -13;
    end = html.find('/div>', start) +5;
    pageDiv = html[start:end];
    pageDiv = pageDiv.replace("\\t","\t")
    pageDiv = pageDiv.replace("\\r\\n","")
    pageDiv = pageDiv.replace("\\/","/")
    pageDiv = pageDiv.replace('\\"','"')
    soup = BeautifulSoup(pageDiv);
    pageBtn = soup.findAll('a', 'S_bg1');
    if len(pageBtn) > 0:
        return pageBtn[-1].contents[0]
    else:
        return 0
    

#get User list from html -- Start
def getUserList(html):
    start = html.find('cnfList') - 12;
    end = html.find('W_pages') - 27;
    weiboUl = html[start:end];
    weiboUl = weiboUl.replace("\\t","\t")
    weiboUl = weiboUl.replace("\\r\\n","")
    weiboUl = weiboUl.replace("\\/","/")
    weiboUl = weiboUl.replace('\\"','"')
    soup = BeautifulSoup(weiboUl)
    weiboLi = soup.findAll("li")
    result = []
    for eachUser in weiboLi:
        #parse uid,nikename,sex
        reg = re.compile('^.+?uid=(?P<id>[^ ]*)&amp;fnick=(?P<nickName>[^ ]*)&amp;sex=(?P<sex>[^ ]*)".+?')
        regMatch = reg.match(str(eachUser))
        linebits = regMatch.groupdict()
        result.append(linebits);
    return result

#get accountID from html
def getAccountID(html):
    start = html.find('pftb_ul') - 12
    end = html.find('/ul>', start) + 4
    weiboTab = html[start:end]
    weiboTab = weiboTab.replace("\\t","\t")
    weiboTab = weiboTab.replace("\\r\\n","")
    weiboTab = weiboTab.replace("\\/","/")
    weiboTab = weiboTab.replace('\\"','"')
    soup = BeautifulSoup(weiboTab)
    aList = soup.findAll('a');
    if len(aList) == 0:
        return 0;
    else:
        reg = re.compile('^.+?\/p\/(?P<accountID>[^ ]*)\/home.+?')
        regMatch = reg.match(str(aList[0]))
        linebits = regMatch.groupdict()
        return linebits['accountID']

#read users from database
cursor.execute("select * from user")
userTable = cursor.fetchall()
unfetchedUser = [];
allUser = [];
newUser = [];
for row in userTable:
    tmp = User()
    tmp.id = row[0]
    tmp.accountID = row[1]
    allUser.append(long(row[0])) #all user
    if row[3]==0:
        unfetchedUser.append(tmp); #unfetched user
if len(unfetchedUser) == 0:
    print '[info] no unfetched user,exit.'
    exit()

#Start fetch users
for eachUser in unfetchedUser:
    #ingore the cookie owner
    if eachUser.id == MY_UID:
        continue;
    print '[info]Start fetch: UID - ' + str(eachUser.id) + '...'
    
    #fetch follow, get accountID by the way
    print '[info]Fetch Follow Page1...'
    FOLLOW_INIT_PATH = "http://weibo.com/" + str(eachUser.id) + "/follow?refer=usercard&wvr=5&from=usercardnew"
    rawcontents = fetchUrl(FOLLOW_INIT_PATH)
    followPageNum = getPageNum(rawcontents)
    followList = getUserList(rawcontents)
    eachUser.accountID = getAccountID(rawcontents)  #get current user's accountID
    FOLLOW_PATH = "http://weibo.com/p/" + str(eachUser.accountID) + "/follow?page="
    print '[info]Found User Num: ' + str(len(followList))
    if(followPageNum > 1):
        for x in range(2, int(followPageNum) + 1):
            time.sleep(2)
            print '[info]Fetch Follow Page' + str(x) + '...'
            rawcontents = fetchUrl(FOLLOW_PATH + str(x))
            tmpList = getUserList(rawcontents)
            print '[info]Found User Num: ' + str(len(tmpList))
            if len(tmpList) == 0:
                print '[warning]fetch user fail, beak'
                break;
            followList.extend(tmpList)
    #update db
    print '[info]Found Follow User Num: ' + str(len(followList))
    for follow in followList:
        if long(follow['id']) not in allUser:
            sql = "insert into user values(%s,'',%s,0,%s)"
            cursor.execute(sql, [follow['id'], follow['nickName'], follow['sex']])
            allUser.append(long(follow['id']));
        sql = "insert into relation values(null,%s,%s)"
        cursor.execute(sql, [eachUser.id, follow['id']])
    db.commit()
    
    #fetch fans
    print '[info]Fetch Fans Page1...'
    FANS_PATH = "http://weibo.com/p/" + str(eachUser.accountID) + "/follow?relate=fans&page="
    rawcontents = fetchUrl(FANS_PATH + "1")
    fansPageNum = getPageNum(rawcontents)
    fansList = getUserList(rawcontents)
    print '[info]Found User Num: ' + str(len(followList))
    
    if(fansPageNum > 1):
        for x in range(2, int(fansPageNum) + 1):
            time.sleep(2)
            print '[info]Fetch Fans Page' + str(x) + '...'
            rawcontents = fetchUrl(FANS_PATH + str(x))
            tmpList = getUserList(rawcontents)
            print '[info]Found User Num: ' + str(len(tmpList))
            if len(tmpList) == 0:
                print '[warning]fetch user fail, beak'
                break;
            fansList.extend(tmpList)
    #update db
    print '[info]Found Fans User Num: ' + str(len(fansList))
    for fan in fansList:
        if long(fan['id']) not in allUser:
            sql = "insert into user values(%s,'',%s,0,%s)"
            cursor.execute(sql, [fan['id'], fan['nickName'], fan['sex']])
            allUser.append(long(fan['id']));
        sql = "insert into relation values(null,%s,%s)"
        cursor.execute(sql, [fan['id'], eachUser.id])
    db.commit()
    print allUser
	
    #Lastly, update current user
    sql = "update user set accountID=%s,isfetched=1 where id=%s";
    cursor.execute(sql, [eachUser.accountID, eachUser.id])
    db.commit()
#close db
cursor.close()
db.close()
