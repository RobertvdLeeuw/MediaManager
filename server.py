import player, filemanager
import socket, sys, os
from pathlib import Path

def CheckArgumentAmount(expectedlength, arguments):
    if len(arguments) < expectedlength:
        print("Not enough arguments.")
    elif len(arguments) > expectedlength:
        print("Too many arguments.")

    return len(arguments) == expectedlength

def ServerRun(basefolder):  # Only ever plan on 1 client connecting at a time, so no need for threading.
    #conn, addr = s.accept()

    currentFolder = Path(str(basefolder)).relative_to(basefolder)  # CD inspired system, using the relative path starting from basefolder

    while True:
        #data = connection.recv(4096)
        data = input()

        if not data:  # If it's empty
            continue

        data = data.split()  # Seems cleaner to work with than "if data[0] == ...".

        match data[0]:
            #File stuff
            case "select:":  # To select folder: "select <foldername>"'
                if not CheckArgumentAmount(2, data):
                    continue

                if (currentFolder / data[1]).is_dir():
                    currentFolder = currentFolder / data[1]
                    print(f'Moved to folder {data[1]}.')
                elif (currentFolder / data[1]).exists():
                    print("That isn't a folder.")
                else:
                    print("Folder not found.")

            case "up:":  # To move 1 or more folders up or back to base folder: "up: 1/2/3/etc/base"'
                if not CheckArgumentAmount(2, data):
                    continue

                folderlayer = len([x for x in str(currentFolder).split('/') if x])  # 0 is base

                if folderlayer == 0:
                    print("Already in base folder.")
                elif data[1] == "base":
                    currentFolder = Path(str(basefolder)).relative_to(basefolder)
                elif int(data[1]) > folderlayer:
                    print('Too far up. Use "base" as argument to move back to base folder.')
                else:
                    currentFolder = currentFolder.parents[int(data[1]) - 1]

            case "list:":  # To see all files/folders in folder: "list all/folders/files"'
                if not CheckArgumentAmount(2, data):
                    continue

                filemanager.ListItems(currentFolder, data[1])

            case "createfolder:":  # To create folder: "createfolder: <foldername>"'
                if not CheckArgumentAmount(2, data):
                    continue

                filemanager.CreateFolder(currentFolder, data[1])

            case "search:":  # To search for folder/item: "search: <keyword>"'
                if not CheckArgumentAmount(2, data):
                    continue

                filemanager.Search(currentFolder, data[1])

            case "move:":  # To move file/folder: "move: <filename/foldername> <file or folder>"
                if not CheckArgumentAmount(3, data):
                    continue

                to = basefolder / data[2]
                filemanager.MoveItem(currentFolder, data[1], to)

            case "moveall:":  # To move all files in current folder: "moveall: <folder>"
                if not CheckArgumentAmount(2, data):
                    continue

                to = basefolder / data[1]
                filemanager.MoveAll(currentFolder, to)

            case "download:":  # To download: "download: <url> <name> [to]" Goes to currddir if no to argument
                pass

            case "rename:":  # To rename file or folder: "rename: <file> <newname>"
                if not CheckArgumentAmount(3, data):
                    continue

                filemanager.RenameItem((currentFolder / data[1]), data[2])

            case "delete:":
                if not CheckArgumentAmount(2, data):
                    continue

                filemanager.DeleteItem(currentFolder, data[1])

            case "current":
                if not CheckArgumentAmount(1, data):
                    continue

                print('/' + str(currentFolder))

            # Media stuff
            case "play:":  # To play video: "play: <filename>"
                pass

            case "playpause":  # To play/pause: "playpause"
                pass

            case "next:":  # To go to next video: "next"
                pass

            case "stop":  # To stop and turn off video: "stop"
                pass

            case "addqueue:":  # To add to queue: "addqueue: *<filename/foldername>"
                pass

            case "clearqueue":  #  To clear queue: "clearqueue"
                pass

            case "viewqueue":  # To view queue: "viewqueue"
                pass

            case "volume:":  # To change volume: "volume: <0-100>"
                pass


            # Other stuff
            case "help":
                pass

            case _:  # If command isn't recognized, send back "Invalid command"
                print("Invalid argument.")


def CheckOptions(port, basefolder):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', port)) != 0:
            print("Port is already in use.")
            sys.exit()

    if not os.path.isdir(basefolder):
        print("Invalid base folder.")
        sys.exit()


def ServerSetup(port, basefolder):
    CheckOptions(port, basefolder)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostbyname(socket.gethostname()), port))  # Intended to only be used on LAN.
    s.listen(32)

    ServerRun(s)

if __name__ == "__main__":
    basefolder = Path(sys.argv[1])

    #ServerSetup(sys.argv[1], sys.argv[2]);
    ServerRun(basefolder)
