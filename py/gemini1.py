from google import genai

# 1. 這裡的 '你的金鑰' 請記得替換成你真正的 API Key（要用引號包起來）
client = genai.Client(api_key='AIzaSyBMC0b9kKQMHiVLf3uy_3UclrJDrlbKiUg') 

# 直接體驗最新一代的 3.5 Flash
# 2. 修正：把括號裡面那串錯誤的字串刪掉
response = client.models.generate_content(
    model='gemini-3.5-flash',
    contents='打上你要問的問題',
)

print(response.text)