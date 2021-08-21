import downloader
from argumenthandler import TFCheck, FolderCheck

from pathlib import Path
import shutil, os, re

searchResults = list()

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


def DownloadItem(url, to, name):  # Do I need more options?
    if 'youtube' in url:
        downloader.YouTube(url, to, name)
    else:
        downloader.Torrent(url, to, name)


def Search(folder, keyword, fullmatch):
    global searchResults

    searchResults = list()
    counter = 0

    if (fullmatch := TFCheck(fullmatch)) is None:
        return

    if regex := re.match('r".*"', keyword):  # r"..." for regex.
        keyword = keyword.split('"')[1]

    for child in folder.glob('**/*'):
        if regex:
            if fullmatch:
                if not re.fullmatch(keyword, str(child.name)):
                    continue
            else:
                if not re.match(keyword, str(child.name)):
                    continue
        else:
            if fullmatch:
                if not keyword == str(child.name):
                    continue
            else:
                if not keyword in str(child.name):
                    continue
        counter += 1

        print(f"  {counter - 1}: /{str(child.relative_to(folder))}")
        searchResults.append(child)
    print(f"{counter} matches." + (" Use 'goto: <index>' to go to result." if len(searchResults) > 0 else ""))  # Add search queue explanation.


def GoTo(index):  # Index is 0 based
    global searchResults

    if not index.isnumeric():
        print("Invalid index.")
        return

    if int(index) >= len(searchResults):
        print("Index outside of list.")
        return

    destination = searchResults[int(index)]

    return destination if destination.is_dir() else destination.parent


def GetSearchResults(indexes = 0):
    global searchResults

    if indexes == 0:  # No indexes, so all.
        return searchResults

    results = list()

    for index in indexes:
        try:
            if re.match(r"[0-9]*::", index):
                index = int(index.split(':')[0])

                results.extend(searchResults[index::])
            elif re.match(r"[0-9]*:[0-9]*", index):
                indexone, indextwo = index.split(':')

                results.extend(searchResults[int(indexone):int(indextwo)])
            elif index.isnumeric():
                results.append(searchResults[int(index)])
            else:
                print('Invalid index(es).')
                return
        except IndexError:
            print('Invalid index(es).')
            return
    return results


def ListItems(basefolder, folder, type, recursive):
    counter = 0

    if (recursive := TFCheck(recursive)) is None:
        return

    for child in (basefolder / folder).glob('**/*' if recursive else '*'):
        match type:
            case 'all':
                print(f"  /{str(child.relative_to(basefolder))}")
                counter += 1

            case 'folders':
                if child.is_dir():
                    print(f"  /{str(child.relative_to(basefolder))}")
                    counter += 1

            case 'files':
                if not child.is_dir():
                    print(f"  /{str(child.relative_to(basefolder))}")
                    counter += 1

            case _:
                print('Invalid argument. Expected all, folders or files.')
                return

    if counter == 0:
        print(f"No {type} found.")


def FolderUp(baseFolder, currentFolder, amount):
    folderlayer = len([x for x in str(currentFolder).split('/') if x])  # 0 is base

    if (baseFolder / currentFolder) == baseFolder:  # Doesn't like the basefolder
        print("Already in base folder.")
    elif amount == "base":
        return Path(str(baseFolder)).relative_to(baseFolder)
    elif int(amount) > folderlayer:
        print('Too far up. Use "base" as argument to move back to base folder.')
    else:
        return currentFolder.parents[int(amount) - 1]


def CreateFolder(folder, newname):
    try:
        os.mkdir(str(folder.absolute()) + f"/{newname}")
        print(f"Successfully created folder {newname}.")
    except:
        print(f"Failed to create folder {newname}.")
