import os


class Config:
    SECRET_KEY: str = os.environ.get(
        "SECRET_KEY", "dev-key-change-in-production")


class DevelopmentConfig(Config):
    DEBUG: bool = True


class ProductionConfig(Config):
    DEBUG: bool = False


config: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
