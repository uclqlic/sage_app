import requests
import os
import json

# ✅ 直接手动填入你的 Supabase 信息
supabase_url = "https://nalqokxglpfvtsopujzh.supabase.co"  # ← 替换成你的
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hbHFva3hnbHBmdnRzb3B1anpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMzNDY0NjAsImV4cCI6MjA2ODkyMjQ2MH0.7EfEIhDdtcTQL54VLiEGHwrfImnp6E4vPmq0uYRMl0Y"                  # ← 替换成你的

headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json"
}

md_folder = "/Users/liqingyun/Documents/Dao_AI/Dao_AI/book_markdown"

for filename in os.listdir(md_folder):
    if filename.endswith(".md"):
        title = os.path.splitext(filename)[0]
        with open(os.path.join(md_folder, filename), "r", encoding="utf-8") as f:
            content = f.read()

        data = {
            "title": title,
            "file_name": filename,
            "content_md": content,
        }

        response = requests.post(f"{supabase_url}/rest/v1/Chinese_Traditional_Books", headers=headers, data=json.dumps(data))
        if response.status_code in [200, 201]:
            print(f"✅ 成功上传：{filename}")
        else:
            print(f"❌ 上传失败：{filename}，错误：{response.status_code} - {response.text}")
