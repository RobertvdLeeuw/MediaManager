from argumenthandler import TFCheck, FolderCheck

from subprocess import call
from queue import Queue
#import vlc

queue = Queue(maxsize=2048)
currentVideo = None


def GetVideoInfo(path):  # Use ffmpeg module for this (not inhouse).
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

    Stop()

    pass


def PlayFrom(basefolder, recursive, *folders):
    ClearQueue()
    Stop()

    if (recursive := TFCheck(recursive)) is None:
        return

    for folder in folders():
        if FolderCheck(basefolder, folder, item):
            for video in item.glob('**/*' if recursive else '*'):
                queue.put(video)


def AddToQueue(folder, override, recursive, *items):  # Could be video(s) or folder(s)?
    global queue

    if (override := TFCheck(override)) is None:
        return
    elif override:
        ClearQueue()
        Stop()

    if 'search' not in recursive:  # If you want to add from the search results the third argument, for which recursion isn't needed.
        if (recursive := TFCheck(recursive)) is None:
            return

    for item in items:
        item = item[0]  # Because, for some reason, iterating over the args returns a list of len=0 for each arg.

        if (folder / item).exists():
            if (folder / item).is_dir():  # Folders
                for video in item.glob('**/*' if recursive else '*'):
                    queue.put(video)
            else:  # Files
                queue.put(item)
    PlayVideo(queue.get())  # Playing the first enqueued video.


def ClearQueue():
    global queue

    queue = Queue(maxsize=2048)


def ViewQueue():
    global queue

    items = list(queue.queue)

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
