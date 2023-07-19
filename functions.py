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
    title = title.lower().title()
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


def preamble_element_start(line: str,
                           preamble_elements: list) -> bool:
    """
    This function checks to see if a line of text starts with a preamble
    element, returning True if so, False if not.
    :param line: str
    :param preamble_elements: list of str
    :return: bool
    """
    print(f"line: {line}")
    for item in preamble_elements:
        print(f"item: {item}")
        if line.startswith(item):
            return True
    return False


def convert_preamble(lines: list,
                     preamble_length: int,
                     preamble_elements: list) -> list:
    """
    This function converts the entire preamble of the lines and return lines with
    the changes and returns only the preamble.
    This is a new version for branch preamble-paragraphs to fix a long running major
    bug in which paragraphs in the preamble are not parsed into paragraphs. A branch
    was needed because this change could overhaul the naive algorithms used in this
    function.
    :param lines: list of str
    :param preamble_elements: list
    :param preamble_length: int
    :return: list of str
    """
    converted_lines = []
    checked_lines = []
    # The first line is always the name of the spell or item.
    checked_lines.append(lines[0].strip())
    index = 1

    # The second line is either the type of spell or the quality
    # of the item. It should be italicized, but it can run more than
    # one line. We cannot count on any of these lines having typical
    # paragraph endings.
    current_line = lines[index]
    new_line = ""
    while not preamble_element_start(current_line, preamble_elements):
        new_line = f"{new_line}{current_line} "
        print(f"new_line: {new_line}")
        index += 1
        try:
            current_line = lines[index]
            print(f"current_line: {current_line}")
        except IndexError:
            break
    checked_lines.append(new_line.strip())

    # Next, we need to find paragraphs. With spells and magic items,
    # the preamble should have names at the start of every line. Any
    # line that does not start with a preamble element should be part
    # of the previous element.
    print(f"lines: {lines}")

    while index < preamble_length:
        new_line = f"{current_line} "
        index += 1
        print(f"index: {index}. new_line: {new_line}")
        try:
            current_line = lines[index]
            while not preamble_element_start(current_line, preamble_elements):
                new_line = f"{new_line}{current_line} "
                print(f"new_line: {new_line}")
                index += 1
                try:
                    current_line = lines[index]
                    print(f"current_line: {current_line}")
                except IndexError:
                    break
        except IndexError:
            checked_lines.append(new_line.strip())
            print(f"checked_lines: {checked_lines}")
            break
        checked_lines.append(new_line.strip())
        print(f"checked_lines: {checked_lines}")

    for idx, line in enumerate(checked_lines):
        if idx == 0:
            # Add boldface to title.
            converted_lines.append(convert_title(checked_lines[0]))
        elif idx == 1:
            # Add italics to spell type and level (2nd line).
            converted_lines.append(italicize_line(checked_lines[1]))
        elif 1 < idx < preamble_length:
            for item in preamble_elements:
                if checked_lines[idx].startswith(item):
                    converted_lines.append(checked_lines[idx].replace(item, f"__{item}__"))
            print(f"checked line: {checked_lines[idx]}")
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
                paragraphs.append(current_paragraph.strip())
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
    print(f"line: {line}")
    for extra in extras:
        line = line.strip()
        print(f"line: {line}")
        print(f"extra: {extra}")
        if line.startswith(extra):
            return extra
    return None


def write_new_file(lines: list,
                   filepath,
                   dest_folder):
    """
    This function writes a list of strings to disk, adding break lines for each
    string.
    :param lines: list of str
    :param filepath: str, filepath to original file
    :param dest_folder: str
    :return: None or Error string
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


def touch_up_paragraphs(paragraphs: list,
                        emphasis: list,
                        strong_emphasis: list) -> list:
    """
    This function takes a list of paragraphs from the spell description and
    add emphasis to words or phrases matching items in emphasis list or strong
    emphasis for the same in the strong_emphasis list. Then, it returns this
    list when completed.
    :param paragraphs: list of str
    :param emphasis: list of str
    :param strong_emphsis: list of str
    :return: list of str
    """
    for idx, paragraph in enumerate(paragraphs):
        print(f"idx: {idx}. paragraph; {paragraph}")
        print("Emphasis checks.")
        for item in emphasis:
            print(f"item: {item}")
            if item in paragraph:
                # Due to a bug in the way a more naive algorithm performed this
                # operation, I need to make sure that the item has a space before
                # it before changing it.
                if f" {item}" in paragraph:
                    paragraphs[idx] = paragraphs[idx].replace(item, f"_{item}_")
                    print(f"new paragraph: {paragraphs[idx]}")
                else:
                    continue
        print("Strong emphasis checks.")
        for item in strong_emphasis:
            print(f"item: {item}")
            if item in paragraph:
                # Due to a bug in the way a more naive algorithm performed this
                # operation, I need to make sure that the item has a space before
                # it before changing it.
                if f" {item}" in paragraph:
                    paragraphs[idx] = paragraphs[idx].replace(item, f"__{item}__")
                    print(f"new paragraph: {paragraphs[idx]}")
                else:
                    continue
    return paragraphs


if __name__ == "__main__":
    files = ["originals/Alter Self.txt",
             "originals/Alarm.txt",
             "originals/Detect Thoughts.txt",
             "originals/Protection from Poison.txt"]
    # Standalone tests.
    print(convert_title("title"))
    print(f"Bullet test (should be False: {check_for_bullet('No bullet here.')}")
    print(f"Bullet test (should be true): {check_for_bullet('• a level of fatigue.')}")
    print(load_file("originals/test.csv"))

    # Configuration testing.
    elements = load_elements()
    preamble_items = elements["preamble"]
    extras = elements["extras"]
    emphasis_items = elements["emphasis"]
    strong_emphasis_items = elements["strong emphasis"]
    print(f"elements: {elements}")
    print(f"preamble_items: {preamble_items}")
    print(f"extras: {extras}")
    print(f"emphasis_items: {emphasis_items}")
    print(f"strong emphasis items: {strong_emphasis_items}")

    # Conversion testing.
    for file in files:
        print(f"file: {file}")
        lines = load_file(file)
        lines = [line.strip("\n") for line in lines]
        print(f"lines: {lines}")
        preamble = convert_preamble(lines[0:8], 8, preamble_items)
        print(f"preamble: {preamble}")
        paragraphs = find_paragraphs(lines[8:], extras, True)
        print(f"paragraphs: {paragraphs}")
        touched_up = touch_up_paragraphs(paragraphs, emphasis_items,
                                         strong_emphasis_items)
        print(f"touched_up: {touched_up}")
        test_convert = preamble
        test_convert.extend(touched_up)
        write_new_file(test_convert, file, "output")
