from pathlib import Path
import re

def CheckArgumentAmount(expectedlength, arguments, nomaxargs = False):
    if len(arguments) < expectedlength:
        print("Not enough arguments.")
        return False
    elif len(arguments) > expectedlength and not nomaxargs:
        print("Too many arguments.")
        return False

    return True


def TFCheck(arg):
    if arg.upper() == "T":
        return True
    elif arg.upper() == 'F':
        return False
    else:
        print('Invalid argument (T|F).')
        return None


def FolderCheck(basefolder, folder, subfolder):
    target = (folder / subfolder)

    if not target.exists():
        print(f"Folder '{target.relative_to(basefolder)}' not found")
        return None

    if not target.is_dir():
        print(f"'{target.relative_to(basefolder)}' is not a folder.")
        return None

    return target


def CheckNegative(index):
    negative = index[0] == '-'

    if negative:
        index = index[1::]

    if index.isnumeric():
        index = int(index)
    else:
        index = None

    return (index, negative)
