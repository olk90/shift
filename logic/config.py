import json
from pathlib import Path

from PySide6.QtCore import QObject


class Properties(QObject):
    user_home = Path.home()
    config_directory = Path.joinpath(user_home, ".shift")
    config_file = Path.joinpath(config_directory, "config.json")

    theme_index = 0

    locales = ["English", "Deutsch"]
    locale_index = 0

    def get_themes(self) -> list:
        themes = [self.tr("dark"), self.tr("light")]
        return themes

    def write_config_file(self):
        config_dict = {
            "theme": self.theme_index,
            "locale": self.locale_index
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
        else:
            self.write_config_file()


properties = Properties()


def get_theme_index(config: dict) -> int:
    try:
        return config["theme"]
    except KeyError:
        return 0


def get_locale_index(config: dict) -> int:
    try:
        return config["locale"]
    except KeyError:
        return 0
