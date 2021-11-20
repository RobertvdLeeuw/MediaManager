import downloader
from argumenthandler import TFCheck, FolderCheck, IndexCheck

from threading import Thread
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
        oldname = item.name
        item.rename(str(item.parent / newname))
        print(f"Successfully renamed {oldname} to {newname}.")
    except:
        print(f"Failed to rename {item.name} to {newname}.")


def DownloadItem(url, to, name):  # Do I need more options?
    print(f"Downloading {url} as {to}/{name}.")

    if not FolderCheck(to):
        return

    if 'youtube' in url:
        downloadFunc = downloader.YouTube
    else:
        downloadFunc = downloader.Torrent

    downloadThread = Thread(target=downloadFunc, args=(url, to, name))
    downloadThread.daemon = True;
    downloadThread.start()


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


def GetSearchResults(indexes = None):
    global searchResults

    results = set()

    if indexes == None:  # No indexes, so all.
        if len(searchResults) == 0:
            print('No search results to be added.')
            return

        return searchResults

    if all(index[0] == '-' for index in indexes): # If results only need to be removed according to the query.
        results = set(searchResults)

    for index in indexes:  # - before an index removes it - when present.
        originalindex = index

        try:
            if re.match(r"-?([0-9]+|:):([0-9]+|:)", index):  # From index until index. ':' to indicate beginning or end.
                if negative := index[0] == '-':
                    index = index[1::]

                if index == ':::':  # The funny option.
                    indexone, indextwo = 0, len(searchResults)
                elif re.match(r"-?::[0-9]+", index):
                    indexone, indextwo = 0, IndexCheck(index.split(':')[-1])
                elif re.match(r"-?[0-9]+::", index):
                    indexone, indextwo = IndexCheck(index.split(':')[0]), len(searchResults)
                else:
                    indexone, indextwo = index.split(':')
                    indexone, indextwo = IndexCheck(indexone), IndexCheck(indextwo)


                if indexone is not None and indextwo:  # indexone=0 returns false
                    if indexone >= indextwo:
                        print("Second index has to be larger than first.")
                        return
                    else:
                        newresults = set(searchResults[indexone:indextwo])
                else:
                    raise IndexError
            else:  # Just this index.negative = index[0] == '-'
                if negative := index[0] == '-':
                    index = index[1::]

                index = IndexCheck(index)

                if index:
                    newresults = set([searchResults[index]])  # Turning it into a set of len 1 to use the same logic as above.
                else:
                    raise IndexError

            results = (results - newresults) if negative else (results | newresults)
        except IndexError:
            print(f'Invalid index: {originalindex}.')
            return

    return list(results)


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
    folderlayer = len([x for x in str(currentFolder.relative_to(baseFolder)).split('/') if x])

    if str(currentFolder) == '.':
        print("Already in base folder.")
        return currentFolder

    if int(amount) > folderlayer:
        print('Too far up. Use "base" as argument to move back to base folder.')
        return currentFolder

    if amount == "base":
        return Path(str(baseFolder)).relative_to(baseFolder)

    return currentFolder.parents[int(amount) - 1]


def CreateFolder(folder, newname):
    try:
        os.mkdir(str(folder.absolute()) + f"/{newname}")
        print(f"Successfully created folder {newname}.")
    except:
        print(f"Failed to create folder {newname}.")
