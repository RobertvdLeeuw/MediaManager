import downloader
from pathlib import Path
import shutil, os
#import vlc

def MoveItem(folder, item, to):
    if not os.path.isdir(to):
        print("Destination folder doesn't exist.")
        return

    if (folder / item).exists():
        shutil.move(str((folder / item).absolute()),
            str((to / Path(item).name).absolute()))

        print(f"Moved {item} to {to}.")
    else:
        print("File or folder not found.")

def MoveAll(folder, to):
    for child in folder.glob('*'):
        MoveItem(folder, str(child.relative_to(folder)), to)


def DeleteItem(folder, item):
    if (folder / item).exists():
        if (folder / item).is_dir():
            shutil.rmtree(str((folder / item).absolute()))
            print(f"Removed folder {item}.")
        else:  # Files
            os.remove(str((folder / item).absolute()))
            print(f"Removed file {item}.")
    else:
        print("File or folder wasn't found.")


def RenameItem(item, newname):
    try:
        item.rename(str(item.parent / newname))
        print(f"Successfully renamed {item.name} to {newname}.")
    except:
        print(f"Failed to rename {item.name} to {newname}.")


def DownloadItem(url, to, name):  # Will use downloader.py
    pass


def Search(folder, keyword, *args):
    counter = 0 if len(args) == 0 else args[0]  # If a counter has been passed, use it. Otherwise create one (done on original call).

    for child in folder.glob('*'):
        if keyword in str(child.relative_to(folder)):
            print(f"  /{str(child)}")
            counter += 1

        if child.is_dir():
            counter = Search(child, keyword, counter)

    if len(args) == 0:  # Only original call doesn't have counter passed
        print(f"{counter} matches")
    else:
        return counter


def ListItems(folder, type):
    counter = 0

    for child in folder.glob('*'):
        match type:
            case 'all':
                print(f"  /{str(child)}")
                counter += 1

            case 'folders':
                if child.is_dir():
                    print(f"  /{str(child)}")
                    counter += 1

            case 'files':
                if not child.is_dir():
                    print(f"  /{str(child)}")
                    counter += 1

            case _:
                print('Invalid argument. Expected all, folders or files.')
                return

    if counter == 0:
        print(f"No {type} found.")


def CreateFolder(folder, newfoldername):
    try:
        os.mkdir(str(folder.absolute()) + f"/{newfoldername}")
        print(f"Successfully created folder {newfoldername}.")
    except:
        print(f"Failed to create folder {newfoldername}.")
