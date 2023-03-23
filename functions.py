from pathlib import Path
import json

CONFIG = "config/elements.json"


def load_file(filepath):
    """
    This function takes a filepath to a text file and returns a list of lines of
    text contained in the file. It should not be used on any file type other than
    text. It will return an error message if so.
    :param filepath: str
    :return: content: list of str (text lines) or str (error message)
    """
    extension = Path(filepath).suffix
    match extension:
        case ".txt":
            with open(filepath, 'r') as file:
                content = file.readlines()
            return content
        case _:
            return f"{extension} is an invalid format for this program."


def convert_title(title: str) -> str:
    """
    This function adds boldface notation to title of the spell.
    :param title: str
    :return: str
    """
    return f"__{title}__"


def italicize_line(line: str) -> str:
    """
    This function add italics notation to a full line.
    :param line: str
    :return: str
    """
    return f"_{line}_"


def load_elements(config=CONFIG) -> dict:
    """
    This function reads the elements.json file from the config
    directory and returns the dictionary inside it.
    :param config: str, defaults to CONFIG
    :return: elements: dict
    """
    with open(config, 'r') as file:
        content = file.read()
    return json.loads(content)


if __name__ == "__main__":
    print(load_file("originals/Alarm.txt"))
    print(load_file("originals/test.csv"))
    print(convert_title("title"))
    elements = load_elements()
    print(elements)