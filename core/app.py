from core.settings import Settings


class App:

    def __init__(self):

        self.settings = Settings()

    def get_settings(self):

        return self.settings