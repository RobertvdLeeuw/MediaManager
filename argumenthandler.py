from pathlib import Path


def ArgumentAmountCheck(expectedLength: tuple | int, arguments: list, noMaxArgs=False) -> bool:  # Add some sort of dict that has func and args, to specify.
    if isinstance(expectedLength, tuple):
        minArgs, maxArgs = expectedLength

        if len(arguments) < minArgs:
            print("Not enough arguments.")
            return False
        elif len(arguments) > maxArgs:
            print("Too many arguments.")
            return False
        return True

    if len(arguments) < expectedLength:
        print("Not enough arguments.")
        return False
    elif len(arguments) > expectedLength and not noMaxArgs:
        print("Too many arguments.")
        return False
    return True


def TFCheck(arg: str) -> None | bool:
    if arg.upper() not in ("T", "F"):
        print('Invalid argument (T|F).')
        return None
    return arg.upper() == "T"


def FolderCheck(baseFolder: Path, folder: Path) -> None | Path:
    if not folder.exists():
        print(f"Folder '{folder.relative_to(baseFolder)}' not found")
        return None

    if not folder.is_dir():
        print(f"'{folder.relative_to(baseFolder)}' is not a folder.")
        return None

    return folder


def IndexCheck(index: str) -> None | int:
    if index.isnumeric():
        return int(index)
    else:
        return None
