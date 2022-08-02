class Not200Exception(Exception):
    def __init__(self, code, *args):
        super().__init__(*args)
        self.code = code

    def __str__(self):
        return f"Server ansver is not 200 but {self.code}"
