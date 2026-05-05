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