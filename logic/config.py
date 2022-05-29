import json
from pathlib import Path

from PySide6.QtCore import QObject
from sqlalchemy import create_engine as ce
from sqlalchemy.orm import sessionmaker as sm


class Properties(QObject):
    user_home = Path.home()
    config_directory = Path.joinpath(user_home, ".shift")
    config_file = Path.joinpath(config_directory, "config.json")
    database_path = "shift.db"

    theme_index = 0

    locales = ["English", "Deutsch"]
    locale_index = 0

    history_size = 360

    def get_themes(self) -> list:
        themes = [self.tr("dark"), self.tr("light")]
        return themes

    def write_config_file(self):
        config_dict = {
            "theme": self.theme_index,
            "locale": self.locale_index,
            "history_size": self.history_size,
            "database": self.database_path
        }
        config = json.dumps(config_dict, indent=4)
        with open(self.config_file, "w") as f:
            f.write(config)
            f.close()

    def load_config_file(self):
        if not self.config_directory.exists():
            self.config_directory.mkdir()
        if self.config_file.exists():
            file = open(self.config_file)
            config = json.load(file)
            properties.theme_index = get_theme_index(config)
            properties.locale_index = get_locale_index(config)
            properties.history_size = get_history_size(config)
            properties.database_path = get_database(config)
        else:
            self.write_config_file()

    def open_session(self):
        db = ce("sqlite:///" + self.database_path)
        session = sm(bind=db)
        return session()


properties = Properties()


def get_theme_index(config: dict) -> int:
    try:
        return config["theme"]
    except KeyError:
        return properties.theme_index


def get_locale_index(config: dict) -> int:
    try:
        return config["locale"]
    except KeyError:
        return properties.locale_index


def get_history_size(config: dict) -> int:
    try:
        return config["history_size"]
    except KeyError:
        return properties.history_size


def get_database(config: dict) -> str:
    try:
        return config["database"]
    except KeyError:
        return properties.database_path
