import player, filemanager
from argumenthandler import ArgumentAmountCheck, FolderCheck, IndexCheck

import socket, sys, os
from pathlib import Path
from threading import Thread
from getpass import getpass


def ServerRun(baseFolder: Path):  # Only ever plan on 1 client connecting at a time, so no need for threading.
    # conn, addr = s.accept()

    # Does this need that str typecast?
    currentFolder = Path(str(baseFolder)).relative_to(baseFolder)  # CD inspired system, using the relative path starting from baseFolder

    if not currentFolder.is_dir():
        print('Invalid base folder.')
        sys.exit()

    print("Start a path with '/' to show it starts from the base folder. Otherwise it'll be seen as relative to the current folder.")

    endCheckThread = Thread(target=player.CheckVideoEnd)
    endCheckThread.daemon = True
    endCheckThread.start()

    while True:
        # data = connection.recv(4096)
        data = input('> ')

        if not data:  # If it's empty
            continue

        inBase = currentFolder == baseFolder  # Returns '.' if the current folder is the base folder.

        data = data.split()

        match data[0]:
            # File stuff
            case "select:":  # To select folder: "select <foldername>"
                if not ArgumentAmountCheck(2, data):
                    continue

                fromBase = data[1][0] == '/'  # Showing whether it's a relative to current or base folder.
                if fromBase or inBase:
                    folder = baseFolder / data[1][1::] if fromBase else baseFolder / data[1]
                    newFolder = FolderCheck(baseFolder, folder)
                else:
                    newFolder = FolderCheck(baseFolder, currentFolder / data[1])

                if newFolder:
                    currentFolder = newFolder
                    print(f'Moved to folder {data[1]}.')

            case "up:":  # To move 1 or more folders up or back to base folder: "up: 1/2/3/.../base"
                if not ArgumentAmountCheck(2, data):
                    print("up: 1/2/3/.../base")
                    continue

                if not IndexCheck(data[1]):
                    print("Invalid index")
                    continue

                currentFolder = filemanager.FolderUp(baseFolder, currentFolder, data[1])

            case "list:":  # To see all files/folders in folder, recursion option: "list: all/folders/files [recursive]"
                if not ArgumentAmountCheck((2, 3), data):
                    print("list: all/folders/files [recursive]")
                    continue

                filemanager.ListItems(baseFolder, currentFolder, data[1], *data[2::])

            case "createfolder:":  # To create folder: "createfolder: <foldername>"
                if not ArgumentAmountCheck(2, data):
                    print("createfolder: <foldername>")
                    continue

                filemanager.CreateFolder(currentFolder, data[1])

            case "search:":  # To search for folder/item, exact match: "search: <keyword> <T/F> (keyword in r"..." for regex)
                if not ArgumentAmountCheck((2, 3), data):
                    print("search: <keyword> [fullmatch]")
                    continue

                filemanager.Search(baseFolder if inBase else currentFolder, data[1], *data[2::])

            case "goto:":  # To go to a search result: "goto: <index>"
                if not ArgumentAmountCheck(2, data):
                    print("goto: <index>")
                    continue

                if destination := filemanager.GoTo(data[1]):
                    currentFolder = (currentFolder / destination)

            case "move:":  # To move file/folder: "move: <filename/foldername> <file or folder>"
                if not ArgumentAmountCheck(3, data):
                    print("move: <filename/foldername> <destination file/folder>")
                    continue

                to = baseFolder / data[2]
                filemanager.MoveItem(currentFolder, data[1], to)

            case "moveall:":  # To move all files in current folder: "moveall: <folder>"
                if not ArgumentAmountCheck(2, data):
                    print("moveall: <folder>")
                    continue

                to = baseFolder / data[1]
                filemanager.MoveAll(currentFolder, to)

            case "download:":  # To download: "download: <url> [to] [name]" Goes to currdir if no to argument
                if not ArgumentAmountCheck((3, 4), data):
                    print("download: <url> <name> [to]")
                    continue

                filemanager.DownloadItem(baseFolder,
                                         data[1],
                                         currentFolder if data[2] == 'current' else Path(data[2]),
                                         *data[3::])

            case "rename:":  # To rename file or folder: "rename: <file> <newname>"
                if not ArgumentAmountCheck(3, data):
                    print("rename: <file> <newname>")
                    continue

                filemanager.RenameItem((currentFolder / data[1]), data[2])

            case "delete:":  # To delete a folder or an item: "delete <filepath/folderpath>"
                if not ArgumentAmountCheck(2, data):
                    print("delete <filepath/folderpath>")
                    continue

                filemanager.DeleteItem(currentFolder, data[1])

            case "currentfolder":  # To view current folder: "currentfolder"
                print('  \\' + str(currentFolder if inBase else currentFolder.relative_to(baseFolder)))  # Messy, I know. But there isn't really a better solution.

            case "base":  # To see the base folder: "base"
                print(baseFolder)

            # Media stuff
            case "play:":  # To play video: "play: <filename>"
                if not ArgumentAmountCheck((1, 2), data):
                    print("play: <filename>")
                    continue

                if len(data) == 2:
                    player.PlayVideo(str(baseFolder / currentFolder / data[1]))
                else:
                    player.NextVideo()

            case "playfrom:":  # To play from folder(s): "playfrom: [recursive] <filename/foldername>[*]"
                # if not ArgumentAmountCheck((1, 2), data, noMaxArgs=True):
                #     print("playfrom: [recursive] <filename(s)/foldername(s)>")
                #     continue

                player.PlayFrom(baseFolder, currentFolder, *data[1::])

            case "playpause":  # To play/pause: "playpause"
                player.PlayPause()

            case "repeat:":  # To toggle video repeating: "repeat: [state]". No second arguments switches repeat state.
                if not ArgumentAmountCheck((1, 2), data):  # No need for recursive on search
                    print("repeat: [state]")
                    continue
                player.ToggleRepeat(*data[1::])

            case "next:":  # To go to next video: "next"
                player.NextVideo()

            case "stop":  # To stop and turn off video: "stop"
                player.Stop()

            case "addqueue:":  # To add to queue: "addqueue: [override] [recursive] <filename/foldername>[*]"
                if not ArgumentAmountCheck(3 if "search" in data else 4, data, noMaxArgs=True):  # No need for recursive on search
                    print("'addqueue: [override] [recursive] <filename/foldername>[*]' OR 'addqueue: [override] search <index>[*]' for search results")
                    continue

                if "search" in data:  # Queueing last search results, with possible indexes.
                    files = filemanager.GetSearchResults(indexes=data[3::]) if len(data) >= 4 \
                        else filemanager.GetSearchResults()
                else:
                    files = data[3::]

                if files:
                    player.AddToQueue(baseFolder if inBase else currentFolder, data[1], data[2], *files)

            case "clearqueue":  # To clear queue: "clearqueue"
                player.ClearQueue()

            case "viewqueue":  # To view queue: "viewqueue"
                player.ViewQueue()

            case "shufflequeue":  # To shuffle queue: "shufflequeue"
                player.ShuffleQueue()

            case "currentvideo":  # To view queue: "viewqueue"
                player.ViewCurrent()

            case "volume:":  # To change volume: "volume: <0-100>"
                if not ArgumentAmountCheck(2, data):
                    print("volume: <0-100>")
                    continue

                player.ChangeVolume(data[1])  # TODO: https://vitux.com/how-to-turn-off-your-monitor-using-a-python-script-in-ubuntu/

            # Other stuff
            case "help" | "?":
                for line in open('help.txt').readlines():
                    print(line.replace('\n', ''))

            case "close":  # Case closed! Hehe.
                sys.exit()

            case _:  # If command isn't recognized, send back "Invalid command"
                print("Invalid argument. Type 'help' or '?' for help. Did you forget a colon?")


def CheckOptions(port: int, baseFolder: Path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', port)) != 0:
            print("Port is already in use.")
            sys.exit()

    if not baseFolder.is_dir():
        print("Invalid base folder.")
        sys.exit()


def ServerSetup(port: int, baseFolder: Path):
    CheckOptions(port, baseFolder)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostbyname(socket.gethostname()), port))  # Intended to only be used on LAN.
    s.listen(32)

    # ServerRun(s)


if __name__ == "__main__":
    if not ArgumentAmountCheck(3, sys.argv):
        sys.exit()

    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    baseFolder = Path(sys.argv[1])
    passcode = sys.argv[2]
    os.path.isdir(baseFolder)
    if getpass('Enter passcode: ') == passcode:
        # ServerSetup(sys.argv[1], sys.argv[2]);
        ServerRun(baseFolder)
    else:
        print('Invalid code.')
