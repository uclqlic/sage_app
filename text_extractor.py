import pdfplumber
import os

# 设置输入文件夹和输出文件夹路径
input_folder = "/Users/liqingyun/Documents/Dao_AI/传统书籍"
output_folder = "/Users/liqingyun/Documents/Dao_AI/Dao_AI/book_markdown"

# 确保输出目录存在
os.makedirs(output_folder, exist_ok=True)

# 遍历输入文件夹中的所有 PDF 文件
for filename in os.listdir(input_folder):
    if filename.lower().endswith(".pdf"):
        input_path = os.path.join(input_folder, filename)
        book_title = os.path.splitext(filename)[0]
        output_path = os.path.join(output_folder, f"{book_title}.md")

        print(f"📖 正在处理：{filename}")
        all_text = ""

        try:
            with pdfplumber.open(input_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        all_text += f"\n\n## 第{i+1}页\n\n{text.strip()}"

            # 写入 Markdown 文件
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"# {book_title}\n{all_text}")

            print(f"✅ 已保存为 Markdown 文件：{output_path}")
        except Exception as e:
            print(f"❌ 处理 {filename} 时出错：{e}")
