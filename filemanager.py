import downloader
from argumenthandler import TFCheck, FolderCheck, IndexCheck

from threading import Thread
from pathlib import Path
import shutil, os, re


searchResults = list()


def MoveItem(folder: Path, item: str, to: Path):
    if not os.path.isdir(to):
        print("Destination folder doesn't exist.")
        return

    if (folder / item).exists():
        shutil.move(str((folder / item).absolute()),
            str((to / item).absolute()))

        print(f"Moved {item} to {to}.")
    else:
        print("File or folder not found.")


def MoveAll(folder: Path, to: Path):
    for child in folder.glob('*'):
        MoveItem(folder, str(child.relative_to(folder)), to)


def DeleteItem(folder: Path, item: str):
    if (folder / item).exists():
        if (folder / item).is_dir():
            shutil.rmtree(str((folder / item).absolute()))  # Shutil because pathlib and os can only delete empty folders
            print(f"Removed folder {item}.")
        else:  # Files
            os.remove(str((folder / item).absolute()))
            print(f"Removed file {item}.")
    else:
        print("File or folder wasn't found.")


def RenameItem(item: Path, newName: str):
    try:
        oldName = item.name
        item.rename(str(item.parent / newName))
        print(f"Successfully renamed {oldName} to {newName}.")
    except Exception as e:
        print(f"Failed to rename {item.name} to {newName}. Error {e}.")


def DownloadItem(baseFolder: Path, url: str, to: Path, *options):  # Do I need more options?
    if not FolderCheck(baseFolder, to):
        return

    options = list(options)

    if not options:
        print(f"Downloading {url} as {to} with original name.")
        Thread(target=downloader.DownloadManager, args=(baseFolder, url, to)).start()
    else:
        print(f"Downloading {url} as {to}\\{options[0]}.")
        Thread(target=downloader.DownloadManager, args=(baseFolder, url, to, options[0])).start()


def Search(folder: Path, keyword: str, *options):
    global searchResults

    searchResults = list()
    counter = 0

    fullMatch = 'F' if not options else options[0]
    if (fullMatch := TFCheck(fullMatch)) is None:
        return

    if regex := re.match('r".*"', keyword):  # r"..." for regex.
        keyword = keyword.split('"')[1]

    for child in folder.glob('**/*'):
        if regex:
            match = re.fullmatch(keyword, str(child.name)) if fullMatch else re.match(keyword, str(child.name))
        else:
            match = keyword is str(child.name) if fullMatch else keyword in str(child.name)
        if not match:
            continue

        print(f"  {counter}: \\{child.relative_to(folder)}")
        searchResults.append(child)

        counter += 1
    print(f"{counter} matches." + (" Use 'goto: <index>' to go to result." if searchResults else ""))  # Add search queue explanation.


# Returning itself if it's a folder, else the folder it's located in.
def GoTo(index: str) -> None | Path:  # Index is 0 based
    global searchResults

    if not index.isnumeric():
        print("Invalid index.")
        return

    if int(index) >= len(searchResults):
        print("Index outside of list.")
        return

    destination = searchResults[int(index)]

    return destination if destination.is_dir() else destination.parent


def GetSearchResults(indexes=None) -> None | list:
    global searchResults

    results = set()

    if not indexes:  # No indexes, so all.
        if len(searchResults) == 0:
            print('No search results to be added.')
            return

        return searchResults

    if all(index[0] == '-' for index in indexes):  # If results only need to be removed according to the query.
        results = set(searchResults)

    for index in indexes:  # - before an index removes it - when present.
        originalIndex = index

        try:
            if re.match(r"-?([0-9]+|:):([0-9]+|:)", index):  # From index until index. ':' to indicate beginning or end.
                if negative := index[0] == '-':
                    index = index[1::]

                if index == ':::':  # The funny option.
                    indexOne, indexTwo = 0, len(searchResults)
                elif re.match(r"-?::[0-9]+", index):
                    indexOne, indexTwo = 0, IndexCheck(index.split(':')[-1])
                elif re.match(r"-?[0-9]+::", index):
                    indexOne, indexTwo = IndexCheck(index.split(':')[0]), len(searchResults)
                else:
                    indexOne, indexTwo = index.split(':')
                    indexOne, indexTwo = IndexCheck(indexOne), IndexCheck(indexTwo)
                if indexOne is not None and indexTwo:  # indexOne=0 returns false
                    if indexOne >= indexTwo:
                        print("Second index has to be larger than first.")
                        return
                    else:
                        newResults = set(searchResults[indexOne:indexTwo])
                else:
                    raise IndexError
            else:  # Just this index.negative = index[0] == '-'
                if negative := index[0] == '-':
                    index = index[1::]

                index = IndexCheck(index)

                if index:
                    newResults = {searchResults[index]}  # Turning it into a set of len 1 to use the same logic as above.
                else:
                    raise IndexError

            results = (results - newResults) if negative else (results | newResults)
        except IndexError:
            print(f'Invalid index: {originalIndex}.')
            return
    return list(results)


def ListItems(baseFolder: Path, folder: Path, searchType: str, *options):
    counter = 0

    recursive = 'F' if not options else options[0]
    if (recursive := TFCheck(recursive)) is None:
        return

    for child in (baseFolder / folder).glob('**/*' if recursive else '*'):
        match searchType:
            case 'all':
                print(f"  /{str(child.relative_to(baseFolder))}")
                counter += 1

            case 'folders':
                if child.is_dir():
                    print(f"  /{str(child.relative_to(baseFolder))}")
                    counter += 1

            case 'files':
                if not child.is_dir():
                    print(f"  /{str(child.relative_to(baseFolder))}")
                    counter += 1

            case _:
                print('Invalid argument. Expected all, folders or files.')
                return

    if counter == 0:
        print(f"No {searchType} found.")


def FolderUp(baseFolder: Path, currentFolder: Path, amount: str) -> Path:
    folderLayer = len([x for x in str(currentFolder.relative_to(baseFolder)).split('/') if x])

    if amount == "base":
        return baseFolder.relative_to(baseFolder)

    if currentFolder == baseFolder:
        print("Already in base folder.")
        return currentFolder

    if int(amount) > folderLayer:
        print('Too far up. Use "base" as argument to move back to base folder.')
        return currentFolder

    return currentFolder.parents[int(amount) - 1]


def CreateFolder(folder, newName):
    try:
        os.mkdir(str(folder.absolute()) + f"/{newName}")
        print(f"Successfully created folder {newName}.")
    except Exception as e:
        print(f"Failed to create folder {newName}. Error: {e}.")
