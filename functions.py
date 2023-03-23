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


def convert_preamble(lines: list,
                     preamble_length: int,
                     preamble_elements: list) -> list:
    """
    This function converts the entire preamble of the lines and return lines with
    the changes.
    :param lines: list of str
    :param preamble_elements: list
    :param preamble_length: int
    :return: list of str
    """
    converted_lines = []
    for idx, line in enumerate(lines):
        if idx == 0:
            # Add boldface to title.
            converted_lines.append(convert_title(lines[0]))
        elif idx == 1:
            # Add italics to spell type and level (2nd line)
            converted_lines.append(italicize_line(lines[1]))
        elif 1 < idx < preamble_length:
            element_found = False
            for item in preamble_elements:
                if lines[idx].startswith(item):
                    element_found = True
                    new_item = f"__{item}__"
                    converted_lines.append(lines[idx].replace(item, new_item))
            if not element_found:
                converted_lines.append(lines[idx])
        else:
            converted_lines.append(lines[idx])
    print(converted_lines)
    return converted_lines


if __name__ == "__main__":
    print(load_file("originals/Alarm.txt"))
    print(load_file("originals/test.csv"))
    print(convert_title("title"))
    elements = load_elements()
    print(elements)
    lines = load_file("originals/Alarm.txt")
    lines = [line.strip("\n") for line in lines]
    print(convert_preamble(lines, 8, elements["preamble"]))
