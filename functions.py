from pathlib import Path


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


if __name__ == "__main__":
    print(load_file("originals/Alarm.txt"))
    print(load_file("originals/test.csv"))
