class TelegramError:
    def __init__(self, data):
        self.status = data["error"]["status"]
        self.message = data["error"]["message"]