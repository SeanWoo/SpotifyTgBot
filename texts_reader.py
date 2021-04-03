import json

texts = "texts.json"

with open(texts, "r",encoding='utf-8') as f:
    messages = json.loads(f.read())

def hello_msg():
    return messages["help_message"]
def msg(name,lang = "ru"):
    return messages[lang][name]