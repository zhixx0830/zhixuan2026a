import requests
from bs4 import BeautifulSoup

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from flask import Flask, render_template, request, make_response, jsonify

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
    link += "<a href=/road>台中市十大肇事路口</a><hr>"
    link += "<a href=/weather>天氣查詢系統</a><hr>"
    link += "<a href=/rate>本週新片進DB</a><hr>"
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

@app.route("/road", methods=["POST","GET"])
def road():
    R = "<h2>台中市十大肇事路口</h2>" 
    url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"
    
    # 升級版的終極偽裝標頭
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive"
    }

    try:
        # 加上 timeout=10，避免程式卡住等太久
        Data = requests.get(url, verify=False, headers=headers, timeout=10)
        JsonData = json.loads(Data.text)
        
        for item in JsonData:
            R += f"{item['路口名稱']}，總共發生 {item['總件數']} 件事故 <br>"
            
    except Exception as e:
        return f"讀取台中市開放資料失敗，錯誤原因：{e}"

    return R + "<br><br><a href='/'>回首頁</a>"

@app.route("/weather", methods=["GET", "POST"])
def weather():
    if request.method == "POST":
        city = request.form["city"]

        search_city = city.replace("台", "臺")

        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=rdec-key-123-45678-011121314&format=JSON&locationName=" + search_city
        try:
            Data = requests.get(url, verify=False)
            JsonData = json.loads(Data.text)

            Weather = JsonData["records"]["location"][0]["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
            Rain = JsonData["records"]["location"][0]["weatherElement"][1]["time"][0]["parameter"]["parameterName"]

            info = f"<h3>{city} 目前天氣預報</h3>"
            info += f"天氣狀況：{Weather} <br>"
            info += f"降雨機率：{Rain}% <br><br>"
            info += "<a href='/weather'>重新查詢</a> | <a href='/'>回首頁</a>"
            
            return info
            
        except Exception as e:
            return f"查詢失敗，找不到「{city}」的天氣資料，請確認是否有加上「市」或「縣」（例如：台中市、花蓮縣）。<br><br><a href='/weather'>重新查詢</a>"
            
    else:
        return render_template("weather.html")

@app.route("/rate")
def rate():
    #本週新片
    url = "https://www.atmovies.com.tw/movie/new/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    lastUpdate = sp.find(class_="smaller09").text[5:]
    print(lastUpdate)
    print()

    result=sp.select(".filmList")

    for x in result:
        title = x.find("a").text
        introduce = x.find("p").text

        movie_id = x.find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw/movie/" + movie_id
        picture = "https://www.atmovies.com.tw/photo101/" + movie_id + "/pm_" + movie_id + ".jpg"

        r = x.find(class_="runtime").find("img")
        rate = ""
        if r != None:
            rr = r.get("src").replace("/images/cer_", "").replace(".gif", "")
            if rr == "G":
                rate = "普遍級"
            elif rr == "P":
                rate = "保護級"
            elif rr == "F2":
                rate = "輔12級"
            elif rr == "F5":
                rate = "輔15級"
            else:
                rate = "限制級"

        t = x.find(class_="runtime").text

        t1 = t.find("片長")
        t2 = t.find("分")
        showLength = t[t1+3:t2]

        t1 = t.find("上映日期")
        t2 = t.find("上映廳數")
        showDate = t[t1+5:t2-8]

        doc = {
            "title": title,
            "introduce": introduce,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": int(showLength),
            "rate": rate,
            "lastUpdate": lastUpdate
        }

        db = firestore.client()
        doc_ref = db.collection("本週新片含分級").document(movie_id)
        doc_ref.set(doc)
    return "本週新片已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate

@app.route("/webhook", methods=["POST"])
def webhook():
    # 1. 取得 Dialogflow 的請求內容
    req = request.get_json(force=True)
    query_result = req.get("queryResult")
    action = query_result.get("action")
   
    # 初始化回傳訊息開頭
    info = "我是許芷嫙設計的電影聊天機器人。\n"
    db = firestore.client()

    # --- 動作 A：根據「分級」查詢電影 ---
    if action == "rateChoice":
        rate = query_result.get("parameters").get("rate")
        info += f"您選擇查詢的分級是：{rate}\n\n"
       
        # 搜尋資料庫中符合該分級的電影
        collection_ref = db.collection("本週新片含分級")
        # 使用 where 進行精準篩選
        docs = collection_ref.where(filter=FieldFilter("rate", "==", rate)).get()
       
        found = False
        for doc in docs:
            found = True
            m = doc.to_dict()
            info += f"🎬【{m['title']}】\n"
            info += f"📅 上映日期：{m['showDate']}\n"
            info += f"🔗 介紹：{m['hyperlink']}\n\n"
       
        if not found:
            info += f"很抱歉，目前找不到標記為「{rate}」的新片喔。"

    # --- 動作 B：根據「關鍵字」查詢特定欄位 (片名/分級/日期) ---
    elif action == "MovieDetail":
        params = query_result.get("parameters")
        question = params.get("filmq")  # 使用者想查的欄位，如：片名、分級
        keyword = params.get("any")     # 使用者輸入的關鍵字，如：超人
       
        info += f"您要查詢電影的 {question}，關鍵字是：{keyword}\n\n"

        # 欄位映射對照表
        mapping = {
            "片名": "title",
            "分級": "rate",
            "上映日期": "showDate",
            "介紹": "introduce"
        }
        target_field = mapping.get(question, "title")

        collection_ref = db.collection("本週新片含分級")
        docs = collection_ref.get()
       
        found = False
        for doc in docs:
            m = doc.to_dict()
            # 模糊搜尋：關鍵字是否出現在該欄位中
            if keyword in str(m.get(target_field, "")):
                found = True
                info += f"🎬 片名：{m['title']}\n"
                info += f"🎥 分級：{m['rate']}\n"
                info += f"⏳ 片長：{m['showLength']} 分鐘\n"
                info += f"📅 上映日期：{m['showDate']}\n"
                info += f"🔗 介紹網址：{m['hyperlink']}\n\n"
       
        if not found:
            info += f"在【{question}】中找不到包含「{keyword}」的電影。"

    # 若 action 都不符合
    else:
        info += "我不太明白您的意思，您可以試試說「我想查普遍級電影」或「查詢片名有超人的電影」。"

    # 4. 回傳 JSON 給 Dialogflow
    return make_response(jsonify({"fulfillmentText": info}))


if __name__ == "__main__":
    app.run()