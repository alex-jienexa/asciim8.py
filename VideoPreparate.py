from datetime import timedelta
from moviepy.editor import VideoFileClip
import cv2
import numpy as np
import os

class VideoPreparate():
    '''Что делает?
        - Переделывает видео в ч/б формат, для комфортной работы и вывода картинки
        - Режет видео на кадры и сохраняет их в отдельную папку
        - Уменьшает размер изображения до 128 пикселей в ширину (высота сохраняется проворцией), без сохранения качества (для хорошего вывода)
    '''

    VIDEO_FRAMES_PER_SECOND = 16

    def open_video(): #! Открывает первое видео для воспроизведения
        fileDir = r'video' # Открыввем папку с видео
        fileExt = r'.mp4' # Ищем mp4 файлы
        videos = [_ for _ in os.listdir(fileDir) if _.endswith(fileExt)]
        return videos[0]

    def format_time_delta(td): #! Красивый формат времени
        result = str(td)
        try:
            result, ms = result.split('.')
        except ValueError:
            return result + '.00'.replace(':', '-')
        ms = int(ms)
        ms = round(ms / 1e4)
        return f'{result}.{ms:02}'.replace(':', '-')

    def get_saving_frames_durations(video, savingFPS): #! Возращает список длительностей, в которые следует сохранять кадры
        s = []
        try:
            clipDur = video.get(cv2.CAP_PROP_FRAME_COUNT) / video.get(cv2.CAP_PROP_FPS) # получаем продолжительность клипа, разделив количество кадров на количество кадров в секунду
        except ZeroDivisionError:
            clipDur = video.get(cv2.CAP_PROP_FRAME_COUNT) / VideoPreparate.VIDEO_FRAMES_PER_SECOND
        for i in np.arange(0, clipDur, 1 / savingFPS):
            s.append(i)
        return s

    def videoCrop(videoFile): #! Разрезаем видео на кадры
        filename, _ = os.path.splitext(videoFile)
        filename += '-asciim8.py'
        if not os.path.isdir(filename):
            os.mkdir(filename)
        video = cv2.VideoCapture(videoFile)
        fps = video.get(cv2.CAP_PROP_FPS)
        savingFPS = min(VideoPreparate.VIDEO_FRAMES_PER_SECOND, fps)
        savingFramesDurations = VideoPreparate.get_saving_frames_durations(video, savingFPS)
        count = 0
        while True:
            ret, frame = video.read()
            if not ret:
                break #Выйти если нечего читать
            frame_duration = count / fps
            try:
                closest_duration = savingFramesDurations[0]
            except IndexError:
                break
            if frame_duration >= closest_duration:
                frame_duration_formatted = VideoPreparate.format_time_delta(timedelta(seconds=frame_duration))
                cv2.imwrite(os.path.join(filename, f"frame{frame_duration_formatted}.jpg"), frame)
                try:
                    savingFramesDurations.pop(0)
                except IndexError:
                    pass
            count+=1
        video.release()
        VideoPreparate.convertGray(filename)

    def convertGray(videoDir):
        for img in os.listdir(videoDir):
            im = cv2.imread(videoDir+'/'+img, 1)
            im = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
            cv2.imwrite(os.path.join(videoDir, f"{img}-gray.jpg"), im)
        for img in os.listdir(videoDir):
            if not img.endswith("-gray.jpg"):
                os.remove(videoDir+'/'+img)
        

if __name__ == "__main__":  
    import sys
    videoFile = 'is-42.mp4'
    VideoPreparate.videoCrop(videoFile)
    print('Закончил..')