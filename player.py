from argumenthandler import TFCheck, FolderCheck

from subprocess import call
from queue import Queue
#import vlc

queue = Queue()
currentVideo = None


def GetVideoInfo(path):
    global queue

    pass


def PlayPause():
    global currentVideo

    pass


def NextVideo():
    global queue, currentVideo

    pass


def Stop():
    global currentVideo

    pass


def PlayVideo(video):
    global currentVideo

    pass


def PlayFrom(basefolder, recursive, *folders):
    ClearQueue()
    Stop()

    recursive = TFCheck(recursive)

    for folder in folders():
        if FolderCheck(basefolder, folder, item):
            for video in item.glob('**/*' if recursive else '*'):
                queue.put(video)


def AddToQueue(basefolder, override, recursive, *items):  # Could be video(s) or folder(s)?
    global queue

    if TFCheck(override):
        ClearQueue()
        Stop()

    for item in items():
        if (folder / item).exists():
            if (folder / item).is_dir():  # Folders
                for video in item.glob('**/*' if TFCheck(recursive) else '*'):
                    queue.put(video)
            else:  # Items
                queue.put(item)
    PlayVideo(queue.get())  # Playing the first enqueued video.


def ClearQueue():
    global queue

    queue = Queue()


def ViewQueue():
    global queue

    items = list(queue)

    for item in items:
        print(f"  {GetVideoInfo(item)}")


def ChangeVolume(volume):
    try:
        volume = int(volume)
    except:
        print('Incorrect volume argument.')
        return
    finally:
        if 0 <= volume <= 100:
            call(["amixer", "-D", "pulse", "sset", "Master", f"{volume}%"])
        else:
            print('Volume must be between 0 and 100.')
