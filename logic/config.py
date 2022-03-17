import json
from pathlib import Path

from PySide6.QtCore import QObject


class Properties(QObject):
    userHome = Path.home()
    configDirectory = Path.joinpath(userHome, ".shift")
    configFile = Path.joinpath(configDirectory, "config.json")

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
        with open(self.configFile, "w") as f:
            f.write(config)
            f.close()

    def load_config_file(self):
        if not self.configDirectory.exists():
            self.configDirectory.mkdir()
        if self.configFile.exists():
            file = open(self.configFile)
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
