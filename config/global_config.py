class GlobalConfig:
    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalConfig, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get(cls, key, default=None):
        return cls._config.get(key, default)

    @classmethod
    def set(cls, key, value):
        cls._config[key] = value

    @classmethod
    def update(cls, dictionary):
        cls._config.update(dictionary)

    @classmethod
    def clear(cls):
        cls._config.clear()

config = GlobalConfig()
