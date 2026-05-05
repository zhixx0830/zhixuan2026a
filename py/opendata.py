import requests, json
url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"
Data = requests.get(url, verify=False)

Cond = input("請輸入欲查詢的路口關鍵字:")
JsonData = json.loads(Data.text)
for item in JsonData:
    if Cond in item["路口名稱"]:
       print(item["路口名稱"] + ",總共發生" + item["總件數"] + "件事故")
       print()