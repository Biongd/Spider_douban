#coding = utf-8
#获取网页源码
import urllib as u
from urllib import request
#import lxml
from bs4 import BeautifulSoup
#正则表达式
import re
import xlwt
import sqlite3
from flask import Flask

#获取网页html源码
def askurl(url):
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0"}
    req = u.request.Request(url = url, headers = header)

    #设置异常处理
    try:
        respones = u.request.urlopen(req)
        html = respones.read().decode("utf-8")
    except u.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)

    return html

# 从html文件中获取数据
def dataget(html):
    findorder = re.compile(r'<em class="">(\d+)</em>')  ###加括号代表只要括号里的内容，不加的话整个字符串都获取!!!!!!!
    findname = re.compile(r'<span class="title">(.*)</span>')
    findothername = re.compile(r'<span class="other">(.*?)</span>')
    findlink = re.compile(r'<a href="(.*?)">')
    findimg = re.compile(r'<img alt=".*" class="" src="(.*?)" width="100"/>', re.S)
    findcast = re.compile(r'<p class="">(.*?)</p>', re.S)
    findscore = re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>')
    findcount = re.compile(r'<span>(\d*人评价)</span>')
    findinq = re.compile(r'<span class="inq">(.*?)</span>')
    #找到需要的信息模块(通过网页代码看到item包含了我们需要的信息)
    bs = BeautifulSoup(html, "html.parser")        #盛放当前网页数据
    datalist = []
#对每一页的模块进行遍历
    for item in bs.find_all("div",class_= "item"):
         #从item模块中提取我需要的信息
        item = str(item)
        order = re.findall(findorder, item)             #数字可以做成列表用
        order = order[0]
        link = re.findall(findlink, item)[0]            #findall()返回列表,[0]从列表中提取
        name = re.findall(findname, item)
        if len(name) == 1:
            chname = name[0]
            abname = ' '
        else:
            chname = name[0]
            abname = name[1].replace('/','')
            abname = re.sub('\s','',abname,2)
        img = re.findall(findimg, item)[0]
        othername = re.findall(findothername, item)[0]
        othername = re.sub('\s','',othername)
        othername = re.sub('/','',othername,1)
        cast = re.findall(findcast, item)[0]
        cast = re.sub('<br(\s*)?/(\s*)?>', '', cast).strip()
        cast = re.sub('\s','',cast)
        score = re.findall(findscore, item)[0]
        count = re.findall(findcount, item)[0]
        inq = re.findall(findinq, item)
        if len(inq) == 0:
            inq = ' '
        else:
            inq = inq[0].replace('。','')
        data = []
        data.extend([chname, abname, othername, img, link, cast, score, count, inq])
        datalist.append(data)
    return datalist

#遍历每个html文件，每次都调用dataget函数
def alldataget(baseurl):
    #找出规律，获取全部网页源码
    dataall = []
    for i in range(10):
        url = baseurl + str(i*25)
        html = askurl(url)
        datalist = dataget(html)
        dataall.extend(datalist)
    return dataall

#保存到excel：
def save_excel(dataall,path):
    book = xlwt.Workbook(encoding = "utf-8",style_compression=0)
    sheet = book.add_sheet("sheet1", cell_overwrite_ok = True)
    title = ['chname', 'abname', 'othername', 'imglink', 'link', 'cast', 'score', 'count', 'ing']
    for i in range(len(title)):
        sheet.write(0, i ,title[i])
        j=1
        for data in dataall:
            sheet.write(j, i, data[i])
            j = j+1
    savepath = path + 'movie250.xls'
    book.save(savepath)

#创建一个sqlite：
def init_sqlite(path):
    con = sqlite3.connect(path)
    cur = con.cursor()
    # 标签，primary key：组件，autoincrement：自增长
    # varchar 变长字符串，可排序
    sql = '''
        create table movie250
        (id integer primary key autoincrement,     
        chname varchar,                         
        abname varchar,                      
        othername varchar,
        img varchar,
        link varchar,
        cast varchar,
        score varchar,
        count text,
        inq varchar) 
    '''
    #执行并提交到本地
    cur.execute(sql)
    con.commit()
    cur.close()
    con.close()

#将数据填入创建好的sqlite：
def save_sqlite(dataall,path):
    init_sqlite(path)
    con = sqlite3.connect(path)
    cur = con.cursor()
    for data in dataall:
        for i in range(len(data)):
            data[i] = '"'+data[i]+'"'
        data = ','.join(data)
        sql = f'''
            insert into movie250 (chname, abname, othername, img, link, cast, score, count, inq)
            values({data})
        '''
        cur.execute(sql)
    con.commit()
    cur.close()
    con.close()

if  __name__ == "__main__":
    baseurl = "https://movie.douban.com/top250?start="
    path = 'movie250.db'
    dataall = alldataget(baseurl)
    save_excel(dataall, path)
    save_sqlite(dataall, path)
    a1321312135646546
