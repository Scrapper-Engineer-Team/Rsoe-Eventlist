from helpers.input.driver import InputDriver


class StdInputDriver(InputDriver):
    name = "std"

    def __init__(self, i, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.i = i

    def get(self):
        yield {"keyword": self.i}
