from pathlib import Path

def CheckArgumentAmount(expectedlength, arguments, nomaxargs = False):
    if len(arguments) < expectedlength:
        print("Not enough arguments.")
    elif len(arguments) > expectedlength and not nomaxargs:
        print("Too many arguments.")

    return len(arguments) == expectedlength


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
