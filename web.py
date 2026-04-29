import requests
from bs4 import BeautifulSoup

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)

from flask import Flask, render_template, request
from datetime import datetime
import random

app = Flask(__name__)


@app.route("/")
def index():
    link = "<h1>歡迎進入許芷嫙的網站首頁</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>今天日期</a><hr>"
    link += "<a href=/about>關於芷嫙</a><hr>"
    link += "<a href=/welcome?u=芷嫙&dep=靜宜資管>GET傳值</a><hr>"
    link += "<a href=/account>POST傳值(帳號密碼)</a><hr>"
    link += "<a href=/cup>擲茭</a><hr>"
    link += "<a href=/math>數學運算</a><hr>"
    link += "<a href=/read>讀取Firestore資料(根據lab遞減排序,取前4)</a><hr>"
    link += "<a href=/search>老師查詢系統</a><hr>"
    link += "<a href=/movie>查詢即將上映電影</a><hr>"
    link += "<a href=/movie2>讀取開眼電影即將上映影片</a><hr>"
    link += "<a href=/searchQ>關鍵字電影查詢</a><hr>"
    return link

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        # 接收使用者從表單輸入的關鍵字
        keyword = request.form.get("keyword")
        
        db = firestore.client()
        collection_ref = db.collection("靜宜資管2026a")
        docs = collection_ref.get()
        
        results = []
        for doc in docs:
            user = doc.to_dict()
            # 如果名字包含關鍵字，就加入結果清單
            if keyword in user.get("name", ""):
                results.append(user)
        
        # 把結果傳給 HTML 顯示
        return render_template("search.html", results=results, keyword=keyword)
    
    # 如果是直接打開網頁 (GET)，就顯示空的搜尋頁面
    return render_template("search.html")

@app.route("/read")
def read():
    db = firestore.client()

    Temp = ""
    collection_ref = db.collection("靜宜資管2026a")  
    docs = collection_ref.order_by("lab" , direction=firestore.Query.DESCENDING).limit(4).get()  
    
    for doc in docs:
        Temp += str(doc.to_dict()) + "<br>"

    return Temp

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>回到網站首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    year = str(now.year)
    month = str(now.month)
    day = str(now.day)
    now = year + "年" + month + "月" + day + "日"
    return render_template("today.html", datetime=now)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    x = request.values.get("u")
    y = request.values.get("dep")
    return render_template("welcome.html", name = x, dep = y)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route('/cup', methods=["GET"])
def cup():
    #action = request.args.get('action')
    action = request.values.get("action")
    result = None
    
    if action == 'toss':
        x1 = random.randint(0, 1)
        x2 = random.randint(0, 1)
        if x1 != x2:
            msg = "聖筊：表示神明允許、同意，或行事會順利。"
        elif x1 == 0:
            msg = "笑筊：表示神明一笑、不解，或者考慮中，行事狀況不明。"
        else:
            msg = "陰筊：表示神明否定、憤怒，或者不宜行事。"
            
        result = {
            "cup1": "/static/" + str(x1) + ".jpg",
            "cup2": "/static/" + str(x2) + ".jpg",
            "message": msg
        }
        
    return render_template('cup.html', result=result)

@app.route("/math", methods=["GET", "POST"])
def math():
    if request.method == "POST":
        x = request.form["x"]
        opt = request.form["opt"]
        y = request.form["y"]

        x = int(x)
        y = int(y)

        if opt == "/" and y == 0:
            return "除數不能為0"

        else:
            if opt == "+":
                Result = x + y 
            elif opt == "-":
                Result = x - y
            elif opt == "*":
                Result = x * y
            elif opt == "/":
                Result = x / y

        result = f"{x} {opt} {y} 的結果是 {Result}"
        return result
    else:
        return render_template("math.html")

@app.route("/movie")
def movie():
    url = "https://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result = sp.select(".filmListAllX li")

    movie_list = []
    for item in result:
        try:
            # 抓取電影名稱
            title = item.find("img").get("alt")
            # 抓取連結並補上網域
            link = "https://www.atmovies.com.tw" + item.find("a").get("href")
            
            # 將資料放入字典並存進清單
            movie_list.append({"title": title, "link": link})
        except:
            continue

    return render_template("movie.html", movies=movie_list)

@app.route("/movie2")
def movie2():
  url = "http://www.atmovies.com.tw/movie/next/"
  Data = requests.get(url)
  Data.encoding = "utf-8"
  sp = BeautifulSoup(Data.text, "html.parser")
  result=sp.select(".filmListAllX li")
  lastUpdate = sp.find("div", class_="smaller09").text[5:]

  for item in result:
    picture = item.find("img").get("src").replace(" ", "")
    title = item.find("div", class_="filmtitle").text
    movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
    hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
    show = item.find("div", class_="runtime").text.replace("上映日期：", "")
    show = show.replace("片長：", "")
    show = show.replace("分", "")
    showDate = show[0:10]
    showLength = show[13:]

    doc = {
        "title": title,
        "picture": picture,
        "hyperlink": hyperlink,
        "showDate": showDate,
        "showLength": showLength,
        "lastUpdate": lastUpdate
      }

    db = firestore.client()
    doc_ref = db.collection("電影2A").document(movie_id)
    doc_ref.set(doc)    
  return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 

@app.route("/searchQ", methods=["POST","GET"])
def searchQ():
    if request.method == "POST":
        MovieTitle = request.form["MovieTitle"]
        info = ""
        db = firestore.client()      
        collection_ref = db.collection("電影2A")
        docs = collection_ref.order_by("showDate").get()
        
        for doc in docs:
            movie = doc.to_dict()
            if MovieTitle in movie.get("title", ""): 
                info += "片名：" + movie.get("title", "") + "<br>" 
                info += "影片介紹：" + movie.get("hyperlink", "") + "<br>"
                info += "片長：" + movie.get("showLength", "") + " 分鐘<br>" 
                info += "上映日期：" + movie.get("showDate", "") + "<br><br>"            
        
        if info == "":
            return "目前找不到包含「" + MovieTitle + "」的電影喔！<br><a href='/searchQ'>重新查詢</a>"
            
        return info
    else:  
        return render_template("searchQ.html")

if __name__ == "__main__":
    app.run()