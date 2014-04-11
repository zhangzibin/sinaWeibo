# -*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import urllib2
import time
from bs4 import BeautifulSoup
import MySQLdb
import socket
import json

#connect db
db = MySQLdb.connect(host="localhost", user="USER", passwd="PWD", db="sina_weibo")
cursor = db.cursor()
cursor.execute('set names "utf8"')

#config
socket.setdefaulttimeout(10.0)
FP_COOKIE = open("cookies.txt","r")
ARGS_COOKIE = FP_COOKIE.readline()
FP_COOKIE.close()
MY_UID = "YOUR_UID";

#class: User
class User:
    def __init__(self):
        self.id = 0
        self.accountID = ''

#class: Weibo
class Weibo:
    def __init__(self):
        self.weiboID = ''
        self.uid = ''
        self.content = ''
        self.pubTime = ''

#fetch html
def fetchUrl(url):
    try:
        request = urllib2.Request(url);
        request.add_header('Cookie',ARGS_COOKIE)
        response = urllib2.urlopen(request)
        return response.read()
    except:
        print '[error]Fetch html fail'
        return ''

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
        return "0";
    else:
        reg = re.compile('^.+?\/p\/(?P<accountID>[^ ]*)\/home.+?')
        regMatch = reg.match(str(aList[0]))
        try:
            linebits = regMatch.groupdict()
        except:
            return "0"
        return linebits['accountID']

#get weibo list from html
def getWeiboList(html, uid):
    try:
        decodejson = json.loads(html)
        weiboDiv = decodejson['data']
    except:
        return []
    weiboDiv = weiboDiv.replace("\\t","\t")
    weiboDiv = weiboDiv.replace("\\r\\n","")
    weiboDiv = weiboDiv.replace("\\/","/")
    weiboDiv = weiboDiv.replace('\\"','"')
    soup = BeautifulSoup(weiboDiv);
    divList = soup.findAll('div', 'WB_feed_type')
    weiboList = []
    for eachDiv in divList:
        tmpWeibo = Weibo()
        tmpWeibo.uid = uid
        #get mid first
        reg = re.compile('^.+?mid="(?P<mid>[^ ]*)".+?')
        regMatch = reg.match(str(eachDiv))
        try:
            linebits = regMatch.groupdict()
            tmpWeibo.weiboID =  str(linebits['mid'])
        except:
            continue
        #get content
        deList = eachDiv.findAll('div', 'WB_text')
        for eachDe in deList:
            for eachContent in eachDe.contents:
                tmpWeibo.content += str(eachContent)
        #get pubtime
        pubtime = eachDiv.find('a', 'S_link2 WB_time')
        tmpWeibo.pubTime = str(pubtime.contents[0])
        weiboList.append(tmpWeibo)
    return weiboList
    
    

#read user from database
cursor.execute("select * from user where isFetched=1 and isWeibo=0 order by id asc limit 0,1000")
userTable = cursor.fetchall()
for row in userTable:
    #each user, accountID is needed
    tmpUser = User()
    tmpUser.id = str(row[0])
    tmpUser.accountID = str(row[1])
    if tmpUser.accountID == "0":
        time.sleep(2)
        print '[info]User:' + tmpUser.id + 'has no accountID. Get it now'
        FOLLOW_INIT_PATH = "http://weibo.com/" + tmpUser.id + "/follow?refer=usercard&wvr=5&from=usercardnew"
        rawcontents = fetchUrl(FOLLOW_INIT_PATH)
        tmpUser.accountID = getAccountID(rawcontents);
        if tmpUser.accountID == "0":
            '[warning]get accountID fail.'
            continue
    #start fetching
    eachUser = tmpUser
    print '[info]Start fetch ' + eachUser.id + '...'
    # init PATH
    PATH_REAL = "http://weibo.com/p/aj/mblog/mbloglist?id=" + eachUser.accountID + "&page="
    allWeiboList = []
    #fetch 200 page in default
    failTimes = 0
    for page in range(1,100):
        time.sleep(2)
        print '[info]Fetch Page ' + str(page)
        request = urllib2.Request(PATH_REAL + str(page))
        request.add_header('Cookie',ARGS_COOKIE)
        try:
            response = urllib2.urlopen(request)
            rawcontents = response.read()
        except:
            print '[error] Url Read Fail.'
            continue
        tmpList = getWeiboList(rawcontents, eachUser.id)
        print '[info]Num of weibo: ' + str(len(tmpList))
        if len(tmpList) == 0:
            failTimes = failTimes + 1
            if failTimes >= 3:
                print '[info]Fetch user:' + eachUser.id + ' end.'
                break
        else:
            allWeiboList.extend(tmpList)
    #update db
    print '[info]Fetch end. Total fetch: ' + str(len(allWeiboList))
    for eachWeibo in allWeiboList:
        sql = "insert into weibo values(%s,%s,%s,%s,null)"
        try:
            cursor.execute(sql, [eachWeibo.weiboID, eachWeibo.uid, eachWeibo.content, eachWeibo.pubTime])
        except:
            print '[error]insert weibo fail'
            continue
    try:
        cursor.execute("update user set isWeibo=1 where id=" + eachUser.id)
    except:
        print '[error]update user fail'
    db.commit()
    time.sleep(4)
 
#close db
cursor.close()
db.close()




