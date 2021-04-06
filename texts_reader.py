import json

texts = "texts.json"
with open(texts, "r",encoding='utf-8') as f:
    messages = json.loads(f.read())

def get_text(name,lang = "ru"):
    return messages[lang][name]

