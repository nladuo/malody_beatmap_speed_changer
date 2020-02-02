import zipfile
import os
import json
import time
import uuid
from .osu_parser import OsuFileParser
from .music_helper import change_music_speed_with_ffmpeg


def get_tmp_dir():
    with open(os.path.join("upload_dir", "now_dir.txt"), "r") as f:
        return f.read()


def create_tmp_dir():
    _dir = str(uuid.uuid4())
    os.mkdir(os.path.join("upload_dir", "tmp", _dir))

    with open(os.path.join("upload_dir", "now_dir.txt"), "w") as f:
        f.write(_dir)

    return _dir


def get_beatmaps(create=False):
    if create:
        tmp_dir = create_tmp_dir()
    else:
        tmp_dir = get_tmp_dir()

    base_dir = os.path.join("upload_dir", "tmp", tmp_dir)

    beatmaps = []

    with open(os.path.join("upload_dir", "now_file.txt"), "r") as f:
        origin_file_name = f.read()

    mcz_file = os.path.join("upload_dir", "tmp", origin_file_name)

    zFile = zipfile.ZipFile(mcz_file, "r")
    i = 0
    for fileM in zFile.namelist():
        zFile.extract(fileM, base_dir)
        if ".mc" in fileM:
            splits = fileM.split("/")
            if len(splits) != 2:
                raise Exception("error format")
            filepath = os.path.join(base_dir, fileM)
            with open(filepath, "r", encoding="utf-8") as f:
                data = f.read()
            json_data = json.loads(data)

            out_dir = os.path.join(base_dir, splits[0])
            version = json_data["meta"]["version"]
            beatmaps.append({
                "id": i,
                "type": "mc",
                "out_dir": out_dir,
                "version": version,
                # "bpm": bpm,
                "json_data": json_data
            })
            i += 1
        elif ".osu" in fileM:
            filepath = os.path.join(base_dir, fileM)
            json_data = OsuFileParser.read_osu_file(filepath)
            out_dir = base_dir
            version = json_data["Metadata"]["Version"]
            beatmaps.append({
                "id": i,
                "type": "osu",
                "out_dir": out_dir,
                "version": version,
                "json_data": json_data
            })
            i += 1

    return beatmaps


def generate_beatmap_malody(json_data, music_src, speed, outdir):
    tmp_data = json.loads(json.dumps(json_data))

    if "id" in tmp_data["meta"]:
        del tmp_data["meta"]["id"]

    tmp_data["meta"]['version'] += f"-{speed}"  # 修改标题
    print(tmp_data["meta"]['version'])
    tmp_data["meta"]['time'] = int(time.time())  # 修改时间

    for i in range(len(json_data["time"])):  # 修改BPM
        tmp_data["time"][i]["bpm"] = speed * tmp_data["time"][i]["bpm"]

    tmp_data["note"][-1]["offset"] = int(tmp_data["note"][-1]["offset"] / speed)  # 修改偏移


    outfile = f"{int(time.time())}-{speed}.mp3"
    outdest = os.path.join(outdir, outfile)
    change_music_speed_with_ffmpeg(music_src, speed, outdest)

    tmp_data["note"][-1]["sound"] = outfile  # 设置歌曲文件

    outfile = f"{int(time.time())}-{speed}.mc"

    with open(os.path.join(outdir, outfile), "w") as f:
        json.dump(tmp_data, f)


def generate_beatmaps_malody(outdir, json_data, speeds):
    json_data["meta"]["creator"] = "malody_beatmap_speed_changer"
    sond_file = json_data["note"][-1]["sound"]

    music_src = os.path.join(outdir, sond_file)
    for speed in speeds:
        speed = float(speed)
        generate_beatmap_malody(json_data, music_src, speed, outdir)

    tmp_name = get_tmp_dir() + ".mcz"
    tmp_path = os.path.join("upload_dir", tmp_name)

    file_dir = os.path.join("upload_dir", "tmp", get_tmp_dir())

    with zipfile.ZipFile(tmp_path, 'w') as f:
        for _dir in os.listdir(file_dir):
            dir2 = os.path.join(file_dir, _dir)
            if os.path.isdir(dir2):
                for filename in os.listdir(dir2):
                    _path = os.path.join(file_dir, _dir, filename)
                    w_path = os.path.join(_dir, filename)
                    f.write(_path, w_path)

    return tmp_name


def generate_beatmap_osu(json_data, music_src, speed, outdir):
    tmp_data = json.loads(json.dumps(json_data))

    tmp_data["Metadata"]['Version'] += f"-{speed}"  # 修改标题
    print(tmp_data["Metadata"]['Version'])

    tmp_data["General"]["PreviewTime"] = -1

    for i in range(len(json_data["Events"])):  # 修改Events
        splits = tmp_data["Events"][i].split(",")
        if splits[0] == "0":
            splits[1] = str(int(int(splits[1]) / speed))
        elif (splits[0] == "1") or (splits[0] == "Video"):
            splits[1] = str(int(int(splits[1]) / speed))
        elif splits[0] == "2":
            splits[1] = str(int(int(splits[1]) / speed))
            splits[2] = str(int(int(splits[2]) / speed))
        # print(splits)

        tmp_data["Events"][i] = ",".join(splits)

    for i in range(len(json_data["TimingPoints"])):  # 修改TimingPoints
        splits = tmp_data["TimingPoints"][i].split(",")

        splits[0] = str(int(int(splits[0]) / speed))
        splits[1] = str(float(splits[1]) / speed)

        tmp_data["TimingPoints"][i] = ",".join(splits)

    for i in range(len(json_data["HitObjects"])):  # 修改HitObjects
        splits = tmp_data["HitObjects"][i].split(",")

        final_splits = splits[-1].split(":")

        splits[2] = str(int(int(splits[2]) / speed))
        final_splits[0] = str(int(int(final_splits[0]) / speed))
        splits[-1] = ":".join(final_splits)

        tmp_data["HitObjects"][i] = ",".join(splits)

    outfile = f"{int(time.time())}-{speed}.mp3"
    outdest = os.path.join(outdir, outfile)
    change_music_speed_with_ffmpeg(music_src, speed, outdest)

    tmp_data["General"]["AudioFilename"] = outfile  # 设置歌曲文件

    outfile = f"{int(time.time())}-{speed}.osu"

    # 导出.osu文件
    OsuFileParser.write_osu_file(tmp_data, os.path.join(outdir, outfile))


def generate_beatmaps_osu(outdir, json_data, speeds):
    json_data["Metadata"]["Creator"] = "malody_beatmap_speed_changer"
    json_data["Metadata"]["Source"] = "https://github.com/nladuo/malody_beatmap_speed_changer"
    json_data["Metadata"]["Tags"] = "produced by malody_beatmap_speed_changer"
    json_data["Metadata"]["BeatmapID"] = 0
    json_data["Metadata"]["BeatmapSetID"] = -1

    sond_file = json_data["General"]["AudioFilename"]
    music_src = os.path.join(outdir, sond_file)
    for speed in speeds:
        speed = float(speed)
        generate_beatmap_osu(json_data, music_src, speed, outdir)

    tmp_name = get_tmp_dir() + ".osz"
    tmp_path = os.path.join("upload_dir", tmp_name)

    file_dir = os.path.join("upload_dir", "tmp", get_tmp_dir())

    with zipfile.ZipFile(tmp_path, 'w') as f:
        for filepath in os.listdir(file_dir):
            print(filepath)
            _path = os.path.join(file_dir, filepath)
            w_path = filepath
            f.write(_path, w_path)

    return tmp_name


def generate_beatmaps(_type, outdir, json_data, speeds):
    if _type == "mc":
        return generate_beatmaps_malody(outdir, json_data, speeds)
    else:
        return generate_beatmaps_osu(outdir, json_data, speeds)
