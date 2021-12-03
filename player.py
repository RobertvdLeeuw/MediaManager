from argumenthandler import TFCheck, FolderCheck, IndexCheck

from random import shuffle
from vlc import MediaPlayer
from ffprobe import FFProbe

from pathlib import Path
from time import sleep


queue = list()  # List of filepaths
currentVideo = MediaPlayer()
manuallyPaused = False
repeat = False
volume = 100


def CheckVideoEnd():
    global manuallyPaused

    while True:
        sleep(1)

        if currentVideo.get_length() == -1:
            continue

        if not manuallyPaused and not currentVideo.is_playing():
            Stop()
            NextVideo()


def GetVideoInfo(path) -> str:
    # Length, FPS, Title, Resolution
    video = FFProbe(path)

    return path


def PlayPause():
    global currentVideo, manuallyPaused

    if currentVideo.get_length() == -1:
        NextVideo()

    if currentVideo.is_playing():
        currentVideo.pause()
        manuallyPaused = True
    else:
        currentVideo.play()
        manuallyPaused = False


def ViewCurrent():
    global currentVideo

    print(f"  {GetVideoInfo(currentVideo)}")


def ToggleRepeat(*options):
    global repeat

    state = None if not options else options[0]
    if state and TFCheck(state) is None:
        return

    repeat = TFCheck(state) if state else not repeat

    print(f"Turned {'on' if repeat else 'off'} video repeat.")


def NextVideo():
    global queue, repeat, currentVideo

    if not queue:
        print("No video's in queue.")
        return

    PlayVideo(currentVideo if repeat else queue.pop())


def Stop():
    global currentVideo, repeat

    if currentVideo.get_length() == -1:
        print('No video is playing.')
        return

    currentVideo.stop()

    if repeat:
        return

    currentVideo = MediaPlayer()


def PlayVideo(video: str):
    global currentVideo, volume

    if currentVideo.get_length() != -1:
        Stop()

    print(f"Playing '{video}'.")
    currentVideo = MediaPlayer(video)

    currentVideo.play()
    currentVideo.set_fullscreen(True)
    currentVideo.audio_set_volume(volume)


def PlayFrom(baseFolder: Path, currentFolder: Path, *folders):  # options are baked into folders, if present.
    global queue, currentVideo

    ClearQueue()
    if currentVideo.get_length() != -1:
        Stop()

    folders = list(folders)  # Required for popping

    recursive = 'F'
    if folders[0] in ('T', 'F'):
        recursive = folders.pop(0)

    if recursive := TFCheck(recursive):
        return

    if not folders:
        folders.append(baseFolder / currentFolder)

    for folder in folders:
        if FolderCheck(baseFolder, folder):
            for video in folder.glob('**/*' if recursive else '*'):
                if not video.is_dir():
                    queue.append(video)
    NextVideo()


def AddToQueue(folder: Path, *items):  # options are baked into items, if present.
    global queue, currentVideo
    items = list(items)  # Required for popping.

    override = 'F'
    if items[0] in ('T', 'F'):
        override = items.pop(0)

    recursive = 'F'
    if items[0] in ('T', 'F'):
        recursive = items.pop(0)

    if (override := TFCheck(override)) is None:
        return
    elif override:
        ClearQueue()
        Stop()

    if 'search' not in recursive:
        if (recursive := TFCheck(recursive)) is None:
            return

    for item in items:
        if (folder / item).exists():
            if (folder / item).is_dir():  # Folders
                for video in item.glob('**/*' if recursive else '*'):
                    queue.append(video)
            else:  # Files
                queue.append(item)

    if currentVideo.get_length() != -1:
        PlayVideo(queue.pop())  # Playing the first enqueued video.


def ClearQueue():
    global queue

    queue = list()


def ViewQueue():
    global queue

    for index, item in enumerate(queue):
        print(f"  {index}: {GetVideoInfo(item)}")


def ShuffleQueue():
    global queue

    shuffle(queue)


def ChangeVolume(inputVolume: str):
    global currentVideo, volume

    if inputVolume := IndexCheck(inputVolume):
        if 0 <= inputVolume <= 100:
            if currentVideo.get_length() == -1:
                currentVideo.audio_set_volume(inputVolume)

            volume = inputVolume
        else:
            print('Volume must be between 0 and 100.')
    else:
        print('Volume argument is not a number.')
