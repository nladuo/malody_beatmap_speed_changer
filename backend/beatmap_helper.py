import zipfile
import os
import json
import time
import uuid
from .osu_parser import OsuFileParser
from .imd_parser import ImdFileParser
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
            filepath = os.path.join(base_dir, fileM)
            with open(filepath, "r", encoding="utf-8") as f:
                data = f.read()
            json_data = json.loads(data)

            if len(splits) == 1:
                out_dir = base_dir
            else:
                out_dir = os.path.join(base_dir, *splits[:len(splits)-1])
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
            splits = fileM.split("/")
            filepath = os.path.join(base_dir, fileM)
            json_data = OsuFileParser.read_osu_file(filepath)
            if len(splits) == 1:
                out_dir = base_dir
            else:
                out_dir = os.path.join(base_dir, *splits[:len(splits) - 1])
            version = json_data["Metadata"]["Version"]
            beatmaps.append({
                "id": i,
                "type": "osu",
                "out_dir": out_dir,
                "version": version,
                "json_data": json_data
            })
            i += 1
        elif ".imd" in fileM:
            splits = fileM.split("/")
            filepath = os.path.join(base_dir, fileM)
            json_data = ImdFileParser.read_imd_file(filepath)
            if len(splits) == 1:
                out_dir = base_dir
            else:
                out_dir = os.path.join(base_dir, *splits[:len(splits) - 1])
            # version = json_data["Metadata"]["Version"]
            # print(json_data)
            version = json_data["version"]
            beatmaps.append({
                "id": i,
                "type": "rm",
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

    index = 0
    for note in tmp_data["note"]:
        if "offset" in note:
            break
        index += 1
    try:
        tmp_data["note"][index]["offset"] = int(tmp_data["note"][index]["offset"] / speed)  # 修改偏移
    except Exception as e:
        pass

    outfile = f"{int(time.time())}-{speed}.mp3"
    outdest = os.path.join(outdir, outfile)
    change_music_speed_with_ffmpeg(music_src, speed, outdest)

    index = 0
    for note in tmp_data["note"]:
        if "sound" in note:
            break
        index += 1

    tmp_data["note"][index]["sound"] = outfile  # 设置歌曲文件

    outfile = f"{int(time.time())}-{speed}.mc"

    with open(os.path.join(outdir, outfile), "w") as f:
        json.dump(tmp_data, f)


def generate_beatmaps_malody(outdir, json_data, speeds):
    json_data["meta"]["creator"] = "nladuo/malody_beatmap_speed_changer"
    sond_file = ""
    for note in json_data["note"]:
        if "sound" in note:
            sond_file = note["sound"]

    music_src = os.path.join(outdir, sond_file)
    for speed in speeds:
        speed = float(speed)
        generate_beatmap_malody(json_data, music_src, speed, outdir)

    tmp_name = get_tmp_dir() + ".mcz"
    tmp_path = os.path.join("upload_dir", tmp_name)

    file_dir = os.path.join("upload_dir", "tmp", get_tmp_dir())

    with zipfile.ZipFile(tmp_path, 'w') as f:
        write_file_recursively(f, "", file_dir)

    return tmp_name


def write_file_recursively(zfile, relative_dir, base_dir):
    """ 递归搜索文件，并压缩 """
    now_dir = os.path.join(base_dir, relative_dir)
    for filename in os.listdir(now_dir):
        filepath = os.path.join(now_dir, filename)
        if os.path.isdir(filepath):
            write_file_recursively(zfile, os.path.join(relative_dir, filename), base_dir)
        else:
            write_path = os.path.join(relative_dir, filename)
            zfile.write(filepath, write_path)


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
        if float(splits[1]) > 0:
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
    json_data["Metadata"]["Creator"] = "nladuo/malody_beatmap_speed_changer"
    json_data["Metadata"]["Source"] = "https://github.com/nladuo/malody_beatmap_speed_changer"
    json_data["Metadata"]["Tags"] = "produced by nladuo/malody_beatmap_speed_changer"
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
        write_file_recursively(f, "", file_dir)

    return tmp_name


def generate_beatmap_rm(json_data, music_src, speed, outdir):
    tmp_data = json.loads(json.dumps(json_data))

    tmp_data["length"] = int(json_data["length"] / speed)

    print(tmp_data["bpm_list"])
    for i in range(len(json_data["bpm_list"])):  # 修改BPM
        tmp_data["bpm_list"][i]["bpm"] = speed * json_data["bpm_list"][i]["bpm"]
        tmp_data["bpm_list"][i]["t"] = int(json_data["bpm_list"][i]["t"] / speed)

    for i in range(len(json_data["notes"])):  # 修改BPM
        tmp_data["notes"][i]["time"] = int(json_data["notes"][i]["time"] / speed)
        if (json_data["notes"][i]["action"] != 0) and (json_data["notes"][i]["param"] > 3):
            tmp_data["notes"][i]["param"] = int(json_data["notes"][i]["param"] / speed)
            print(tmp_data["notes"][i]["param"])

    outfile = f"{json_data['song_name']}-{speed}.mp3"
    outdest = os.path.join(outdir, outfile)
    change_music_speed_with_ffmpeg(music_src, speed, outdest)

    outfile = f"{json_data['version']}-{speed}.imd"
    outdest = os.path.join(outdir, outfile)
    ImdFileParser.write_imd_file(tmp_data, outdest)


def generate_beatmaps_rm(outdir, json_data, speeds):
    sond_file = json_data["song_file"]

    music_src = os.path.join(outdir, sond_file)
    for speed in speeds:
        speed = float(speed)
        generate_beatmap_rm(json_data, music_src, speed, outdir)

    tmp_name = get_tmp_dir() + ".zip"
    tmp_path = os.path.join("upload_dir", tmp_name)

    file_dir = os.path.join("upload_dir", "tmp", get_tmp_dir())

    with zipfile.ZipFile(tmp_path, 'w') as f:
        write_file_recursively(f, "", file_dir)

    return tmp_name


def generate_beatmaps(_type, outdir, json_data, speeds):
    if _type == "mc":
        return generate_beatmaps_malody(outdir, json_data, speeds)
    elif _type == "rm":
        return generate_beatmaps_rm(outdir, json_data, speeds)
    else:
        return generate_beatmaps_osu(outdir, json_data, speeds)
