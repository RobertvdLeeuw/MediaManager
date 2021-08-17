import downloader
from argumenthandler import TFCheck, FolderCheck

from pathlib import Path
import shutil, os


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
            shutil.rmtree(str((folder / item).absolute()))  # Shutil because pathlib and os can only delete empty folders
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


def DownloadItem(url, to, name):  # Need more options?
    if 'youtube' in url:
        downloader.YouTube(url, to, name)
    else:
        downloader.Torrent(url, to, name)


def Search(folder, keyword):
    counter = 0

    for child in folder.glob('**'):
        if keyword in str(child.relative_to(folder)):
            print(f"  /{str(child.relative_to(folder))}")
            counter += 1
    print(f"{counter} matches")


def ListItems(basefolder, folder, type, recursive):
    counter = 0

    for child in (basefolder / folder).glob('**/*' if TFCheck(recursive) else '*'):
        child = child.relative_to(basefolder)

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


def CreateFolder(folder, newname):
    try:
        os.mkdir(str(folder.absolute()) + f"/{newname}")
        print(f"Successfully created folder {newname}.")
    except:
        print(f"Failed to create folder {newname}.")
