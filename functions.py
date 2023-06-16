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
            try:
                with open(filepath, 'r', encoding="utf-8") as file:
                    content = file.readlines()
                return content
            except FileNotFoundError:
                return f"Error: {filepath} was not found."
        case _:
            return f"Error: {extension} is an invalid format for this program."


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
    the changes and returns only the preamble.
    :param lines: list of str
    :param preamble_elements: list
    :param preamble_length: int
    :return: list of str
    """
    converted_lines = []
    checked_lines = []
    # First, we need to check for prematurely terminated preamble lines.
    i = 0
    # print(f"lines: {lines}")
    while i < preamble_length:
        if check_line_end(lines[i]):
            try:
                new_line = f"{lines[i]} {lines[i+1]}"
                checked_lines.append(new_line)
                i += 2
            except IndexError:
                new_line = f"{lines[i]}"
                checked_lines.append(new_line)
                break
        else:
            checked_lines.append(lines[i])
            i += 1
        print(f"checked_lines: {checked_lines}")

    for idx, line in enumerate(checked_lines):
        if idx == 0:
            # Add boldface to title.
            converted_lines.append(convert_title(checked_lines[0]))
        elif idx == 1:
            # Add italics to spell type and level (2nd line).
            converted_lines.append(italicize_line(checked_lines[1]))
        elif 1 < idx < preamble_length:
            element_found = False
            # print(f"idx: {idx}, preamble_length: {preamble_length}")
            # print(f"element_found: {element_found}")
            for item in preamble_elements:
                # The following fixes a bug in which one preamble item of
                # length X matches the first X characters of another preamble
                # item.
                # print(f"item: {item}")
                # print(f"len(checked_lines): {len(checked_lines)}")
                # print(f"len(converted_lines): {len(converted_lines)}")
                if len(checked_lines) > len(converted_lines):
                    if checked_lines[idx].startswith(item):
                        element_found = True
                        new_item = f"__{item}__"
                        converted_lines.append(
                            checked_lines[idx].replace(item, new_item))
                        print(f"element_found: {element_found}")
                        print(f"new_item: {new_item}")
            if not element_found:
                converted_lines.append(checked_lines[idx])
        print(f"checked_lines: {checked_lines}")
        print(f"converted_lines: {converted_lines}")
    return converted_lines


def check_line_end(line: str) -> bool:
    """
    This function is used to check the end of a line in the preamble to see if is
    prematurely terminated by a list of items split with a comma, colon, or
    semi-colon. Such lines need to be merged. The list of classes and the level
    list can be prematurely terminated.
    :param line: str
    :return: bool
    """
    early_stops = [",", ":", ";", "or", "with"]
    for item in early_stops:
        if line.endswith(item):
            return True
    return False


def find_paragraphs(remaining_txt: list,
                    extras: list,
                    has_extras: bool) -> list:
    """
    This functions receives the remaining text, which will be in the form of
    a list of lines. This text will be returned as assembled paragraphs.
    :param remaining_txt: list of str
    :param extras: list of str
    :param has_extras: bool
    :return: list
    """
    ending_punctuation = [".", "!", "?", ":"]
    current_paragraph = ""
    paragraphs = []
    for line in remaining_txt:
        print(f"current_paragraph: {current_paragraph}")
        # The copying process can leave spaces at the start of a paragraph.
        while line[0] == " ":
            line = line[1:]

        # If a line starts with an extra, the paragraph starts.
        # We also have to add strong emphasis to the extra part.
        extra = identify_extras(line, extras)
        bullet = check_for_bullet(line)
        print(f"extra: {extra}")
        print(f"bullet: {bullet}")
        if has_extras and extra is not None:
            if current_paragraph != "":
                paragraphs.append(current_paragraph)
                current_paragraph = ""
            current_paragraph = line.replace(extra, f"__{extra}__")
            if current_paragraph[-1] in ending_punctuation:
                paragraphs.append(current_paragraph)
        elif bullet:
            if current_paragraph != "":
                paragraphs.append(current_paragraph)
                current_paragraph = ""
            current_paragraph = line.replace("•", "*")
            if current_paragraph[-1] in ending_punctuation:
                paragraphs.append(current_paragraph)
                current_paragraph = ""
        else:
            if current_paragraph != "" and current_paragraph[-1] in ending_punctuation:
                paragraphs.append(current_paragraph)
                current_paragraph = ""
            current_paragraph = current_paragraph + " " + line
            # Paragraphs typically end with the end of a sentence.
            if line[-1] in ending_punctuation:
                paragraphs.append(current_paragraph)
                current_paragraph = ""
        # print(f"current_paragraph: {current_paragraph}")
        # print(f"extra: {extra}")
        print(f"paragraphs: {paragraphs}")

    # Once the initial pass of paragraph generation is done, we need to remove
    # any duplicate first lines. This will correct a bug in which the first line
    # ends with a period or other indicator of the potential end of a paragraph.
    # We can remove these duplicates quite easily.
    paragraphs = check_for_duplication(paragraphs)
    return paragraphs


def check_for_duplication(paragraphs: list) -> list:
    """
    This functions takes a list of text paragraphs and removes duplication of
    all or portions of a paragraph at the beginning of the next paragraph.
    :param paragraphs: list of str
    :return: list of str
    """
    # Duplication produced by the first line ending with a potential paragraph end
    # can be easily fixed by checking lines against the next line.
    no_paragraphs = len(paragraphs)
    checked_paragraphs = []
    index = 0
    while index < no_paragraphs - 1:
        current_paragraph = paragraphs[index]
        next_paragraph = paragraphs[index + 1]
        if current_paragraph not in next_paragraph:
            checked_paragraphs.append(current_paragraph)
        index += 1
        print(f"checked_paragraphs: {checked_paragraphs}")
    checked_paragraphs.append(paragraphs[-1])
    print(f"checked_paragraphs: {checked_paragraphs}")
    return checked_paragraphs


def identify_extras(line: str,
                    extras: list):
    """
    This function checks to see if a line begins with a string in extras. The
    extras are items that start emphasized paragraphs or bullet items in the
    spell description.
    :param line: str
    :param extras: list of str
    :return: str or None
    """
    for extra in extras:
        if line.startswith(extra):
            return extra
    return None


def write_new_file(lines: list,
                   filepath,
                   dest_folder) -> None:
    """
    This function writes a list of strings to disk, adding break lines for each
    string.
    :param lines: list of str
    :param filepath: str, filepath to original file
    :param dest_folder: str
    :return:
    """
    original_filename = Path(filepath).stem
    new_filename = f"__{original_filename}__.txt"
    new_filepath = f"{dest_folder}/{new_filename}"
    output = [line + "\n" for line in lines]
    try:
        with open(new_filepath, 'w') as file:
            file.writelines(output)
        return None
    except FileNotFoundError:
        return f"Error: {dest_folder} was not found."


def check_for_bullet(s: str) -> bool:
    """
    This function checks for a bullet character at the beginning of a string and returns
    True or False depending on the starting character.
    :param s: str
    :return: bool
    """
    return s[0] == "•"


if __name__ == "__main__":
    print(load_file("originals/Alarm.txt"))
    print(load_file("originals/test.csv"))
    print(convert_title("title"))
    elements = load_elements()
    preamble = elements["preamble"]
    extras = elements["extras"]
    print(elements)
    lines = load_file("originals/Alter Self.txt")
    lines = [line.strip("\n") for line in lines]
    print(lines)
    preamble = convert_preamble(lines, 8, elements["preamble"])
    print(preamble)
    paragraphs = find_paragraphs(lines[8:], extras, True)
    print(paragraphs)
    test_convert = preamble
    test_convert.extend(paragraphs)
    write_new_file(test_convert, "originals/Alter Self.txt", "output")
    print(f"Bullet test (should be False: {check_for_bullet('No bullet here.')}")
    print(f"Bullet test (should be true): {check_for_bullet('• a level of fatigue.')}")
