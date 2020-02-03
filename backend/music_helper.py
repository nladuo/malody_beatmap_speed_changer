import os


def change_music_speed_with_ffmpeg(src, speed, dest):
    cmd = f'ffmpeg -n -i "{src}" -filter:a "atempo={speed}" "{dest}"'
    print(cmd)
    os.system(cmd)
