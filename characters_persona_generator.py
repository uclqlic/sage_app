import os
import json
import wikipedia
from openai import OpenAI
from dotenv import load_dotenv

# 加载 API KEY
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 设置 Wikipedia 语言为中文
wikipedia.set_lang("zh")

# 默认保存路径
PERSONA_PATH = "personas.json"

# 初始化 personas 文件
if not os.path.exists(PERSONA_PATH) or os.path.getsize(PERSONA_PATH) == 0:
    personas = {}
else:
    with open(PERSONA_PATH, "r", encoding="utf-8") as f:
        personas = json.load(f)

def fetch_wiki_intro(name):
    try:
        summary = wikipedia.summary(name, sentences=5)
        return summary
    except wikipedia.exceptions.PageError:
        return None
    except wikipedia.exceptions.DisambiguationError as e:
        return f"⚠️ 歧义页面，请更明确人物名：{e.options}"

def generate_persona(name, wiki_summary):
    system = "你是一个文化策展人，擅长根据历史人物简介构建 AI 角色的语言风格和价值观。"
    user_prompt = f"""
以下是人物【{name}】的维基百科简介：

{wiki_summary}

请根据此简介，生成该人物的 AI Agent 设定，格式如下：
{{
  "name": "{name}",
  "english_name": "英文名，如果没有可省略",
  "system_prompt": "你是{name}，讲话风格……价值观……请以{name}的方式回答问题。"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def save_persona(role_id, persona_json_string):
    try:
        persona_data = json.loads(persona_json_string)
        personas[role_id] = persona_data
        with open(PERSONA_PATH, "w", encoding="utf-8") as f:
            json.dump(personas, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存人物：{role_id}")
    except json.JSONDecodeError:
        print("❌ 生成内容无法解析为 JSON，请手动检查：\n", persona_json_string)

if __name__ == "__main__":
    ## 人物选择
    candidates = ["孔子", "老子", "庄子", "南怀瑾", "曾国藩"]

    for name in candidates:
        print(f"\n📌 正在处理：{name}")
        summary = fetch_wiki_intro(name)
        if not summary:
            print(f"❌ 未找到 {name} 的维基百科简介")
            continue
        elif summary.startswith("⚠️"):
            print(summary)
            continue

        print(f"📖 维基简介摘要：\n{summary}\n")
        persona_text = generate_persona(name, summary)
        print(f"🤖 生成角色设定：\n{persona_text}\n")

        save_persona(role_id=name.lower(), persona_json_string=persona_text)
