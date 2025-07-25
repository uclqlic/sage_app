from transformers import AutoTokenizer, AutoModel

model_name = "BAAI/bge-small-zh"
hf_mirror = "https://hf-mirror.com"  # 清华镜像

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, cache_dir="./hf_model", mirror=hf_mirror)
model = AutoModel.from_pretrained(model_name, trust_remote_code=True, cache_dir="./hf_model", mirror=hf_mirror)

print("✅ 成功从镜像加载模型")
