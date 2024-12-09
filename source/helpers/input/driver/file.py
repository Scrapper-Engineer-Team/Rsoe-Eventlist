from helpers.input.driver import InputDriver


class FileInputDriver(InputDriver):
    name = "file"

    def __init__(self, path, *args, **kwargs):
        super(FileInputDriver, self).__init__(*args, **kwargs)
        self.path = path

    def get(self):
        with open(self.path, "r") as f:
            rows = f.readlines()
            for row in rows:
                yield {"keyword": row.replace("\n", "")}
