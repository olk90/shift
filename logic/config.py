import json
from pathlib import Path


class Properties:
    userHome = Path.home()
    configDirectory = Path.joinpath(userHome, ".shift")
    configFile = Path.joinpath(configDirectory, "config.json")

    themes = ["dark", "light"]
    theme_index = 0

    def write_config_file(self):
        config_dict = {
            "theme": self.theme_index
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
        else:
            self.write_config_file()


properties = Properties()


def get_theme_index(config: dict) -> int:
    return config["theme"]
