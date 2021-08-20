import player, filemanager
from argumenthandler import CheckArgumentAmount, FolderCheck

import socket, sys, os
from pathlib import Path


def ServerRun(baseFolder):  # Only ever plan on 1 client connecting at a time, so no need for threading.
    #conn, addr = s.accept()

    currentFolder = Path(str(baseFolder)).relative_to(baseFolder)  # CD inspired system, using the relative path starting from baseFolder

    if not currentFolder.is_dir():
        print('Invalid base folder.')
        sys.exit()

    print("Start a path with '/' to show it starts from the base folder. Otherwise it'll be seen as relative to the current folder.")

    while True:
        #data = connection.recv(4096)
        data = input('> ')

        if not data:  # If it's empty
            continue

        inbase = str(currentFolder) == '.'

        data = data.split()

        match data[0]:
            #File stuff
            case "select:":  # To select folder: "select <foldername>"
                if not CheckArgumentAmount(2, data):
                    continue

                frombase = data[1][0] == '/'
                if frombase or str(currentFolder) == '.':
                    newfolder = FolderCheck(baseFolder, baseFolder, data[1][1::] if frombase else data[1])
                else:
                    newfolder = FolderCheck(baseFolder, currentFolder, data[1])

                if newfolder:
                    currentFolder = newfolder
                    print(f'Moved to folder {data[1]}.')

            case "up:":  # To move 1 or more folders up or back to base folder: "up: 1/2/3/etc/base"
                if not CheckArgumentAmount(2, data):
                    continue

                currentFolder = filemanager.FolderUp(baseFolder, currentFolder, data[1])

            case "list:":  # To see all files/folders in folder, recursion option: "list: all/folders/files <T/F>"
                if not CheckArgumentAmount(3, data):
                    continue

                filemanager.ListItems(baseFolder, currentFolder, data[1], data[2])

            case "createfolder:":  # To create folder: "createfolder: <foldername>"
                if not CheckArgumentAmount(2, data):
                    continue

                filemanager.CreateFolder(currentFolder, data[1])

            case "search:":  # To search for folder/item, exact match: "search: <keyword> <T/F> (keyword in r"..." for regex)
                if not CheckArgumentAmount(3, data):
                    continue

                filemanager.Search(baseFolder if inbase else currentFolder, data[1], data[2])

            case "goto:":  # To go to a search result: "goto: <index>"
                if not CheckArgumentAmount(2, data):
                    continue

                if destination := filemanager.GoTo(data[1]):
                    currentFolder = (currentFolder / destination)

            case "move:":  # To move file/folder: "move: <filename/foldername> <file or folder>"
                if not CheckArgumentAmount(3, data):
                    continue

                to = baseFolder / data[2]
                filemanager.MoveItem(currentFolder, data[1], to)

            case "moveall:":  # To move all files in current folder: "moveall: <folder>"
                if not CheckArgumentAmount(2, data):
                    continue

                to = baseFolder / data[1]
                filemanager.MoveAll(currentFolder, to)

            case "download:":  # To download: "download: <url> <name> [to]" Goes to currdir if no to argument
                if not CheckArgumentAmount(3, data) or CheckArgumentAmount(4, data):  # Work on the error messaeg later (either too many or too few).
                    continue
                pass

            case "rename:":  # To rename file or folder: "rename: <file> <newname>"
                if not CheckArgumentAmount(3, data):
                    continue

                filemanager.RenameItem((currentFolder / data[1]), data[2])

            case "delete:":  # To delete a folder or an item: "delete <filepath/folderpath>"
                if not CheckArgumentAmount(2, data):
                    continue

                filemanager.DeleteItem(currentFolder, data[1])

            case "current":  # To view current folder: "current"
                if not CheckArgumentAmount(1, data):
                    continue

                print('  /' + str(currentFolder if inbase else currentFolder.relative_to(baseFolder)))  # Messy, I know. But there isn't really a better solution.

            case "base":  # To see the base folder: "base"
                print(baseFolder)

            # Media stuff
            case "play:":  # To play video: "play: <filename>"
                if not CheckArgumentAmount(2, data):
                    continue

                player.PlayVideo(data[1])

            case "playfrom:":  # To play from folder(s), recursive: "playfrom: <T/F> <filename/foldername>[*]"
                if not CheckArgumentAmount(3, data, nomaxargs=True):
                    continue

                player.PlayFrom(data[1], data[2::])

            case "playpause":  # To play/pause: "playpause"
                player.PlayPause()

            case "next:":  # To go to next video: "next"
                player.NextVideo()

            case "stop":  # To stop and turn off video: "stop"
                player.Stop()

            case "addqueue:":  # To add to queue, override, recursive: "addqueue: <T/F> <T/F> <filename/foldername>[*]"
                if not CheckArgumentAmount(4, data, nomaxargs=True):
                    continue

                player.AddToQueue(baseFolder if inbase else currentFolder, data[1], data[2], data[3::])

            case "clearqueue":  # To clear queue: "clearqueue"
                player.ClearQueue()

            case "viewqueue":  # To view queue: "viewqueue"
                player.ViewQueue()

            case "volume:":  # To change volume: "volume: <0-100>"
                if not CheckArgumentAmount(2, data):
                    continue

                player.ChangeVolume(data[1])

            # Other stuff
            case ("help"|"?"):
                for line in open('help.txt').readlines():
                    print(line.replace('\n', ''))

            case "close":  # Case closed! Hehe.
                sys.exit()

            case _:  # If command isn't recognized, send back "Invalid command"
                print("Invalid argument. Type 'help' or '?' for help. Did you forget a colon?")


def CheckOptions(port, baseFolder):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', port)) != 0:
            print("Port is already in use.")
            sys.exit()

    if not os.path.isdir(baseFolder):
        print("Invalid base folder.")
        sys.exit()


def ServerSetup(port, baseFolder):
    CheckOptions(port, baseFolder)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostbyname(socket.gethostname()), port))  # Intended to only be used on LAN.
    s.listen(32)

    ServerRun(s)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    baseFolder = Path(sys.argv[1])

    #ServerSetup(sys.argv[1], sys.argv[2]);
    ServerRun(baseFolder)
