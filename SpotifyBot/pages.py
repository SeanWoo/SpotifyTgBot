class PageManager:
    def __init__(self, data):
        self.page = 1
        self.max_pages = 1
        self.chunk = 5
        self.raw_data = list(data)
        self.data = self.cast_to_nav(data)

    def cast_to_nav(self, data):
        nav = {}
        l = 1
        contents_list = []
        while True:
            if len(contents_list) != self.chunk and len(data) != 0:
                contents_list.append(data.pop(0))
            else:
                nav.update([(l, contents_list)])
                contents_list = []
                if len(data) != 0:
                    l += 1
                else:
                    break
        self.max_pages = l
        return nav

    def __getitem__(self, page):
        self.page = page
        return self.data[page]