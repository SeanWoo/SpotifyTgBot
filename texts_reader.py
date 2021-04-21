import json

with open("texts.json", "r", encoding = 'utf-8') as f:
    messages = json.loads(f.read())

languages = list(messages.keys())

def get_text(lang, name):
    return messages[lang][name]

