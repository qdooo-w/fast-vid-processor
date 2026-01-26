import requests
Session = requests.Session()
HEADERS = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
  "Referer": "https://www.bilibili.com"
}

class BilibiliLoginManager:
  """
  B站登录模块 负责cookie获取、保存与校验
  """
  
