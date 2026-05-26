from google import genai

# 1. 這裡的 '你的金鑰' 請記得替換成你真正的 API Key（要用引號包起來）
client = genai.Client(api_key='AIzaSyBMC0b9kKQMHiVLf3uy_3UclrJDrlbKiUg') 

Question = input("請問你要問AI甚麼問題?")

response = client.models.generate_content(
    model='gemini-3.5-flash',
    contents= Question,
)

print(response.text)