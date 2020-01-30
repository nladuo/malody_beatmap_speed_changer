import zipfile
import os
import json
import librosa
import time
import uuid


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

            data = zFile.read(fileM).decode("utf-8")
            json_data = json.loads(data)

            out_dir = os.path.join(base_dir, splits[0])
            version = json_data["meta"]["version"]
            bpm = json_data["time"][0]['bpm']
            beatmaps.append({
                "id": i,
                "out_dir": out_dir,
                "version": version,
                "bpm": bpm,
                "json_data": json_data
            })
            i += 1

    return beatmaps


def generate_song(speed, x, sr, outdir):
    outfile = f"{int(time.time())}-{speed}.wav"
    librosa.output.write_wav(os.path.join(outdir, outfile), x, int(sr * speed))
    return outfile


def generate_beatmap(json_data, x, sr, speed, outdir):
    tmp_data = json.loads(json.dumps(json_data))

    if "id" in tmp_data["meta"]:
        del tmp_data["meta"]["id"]

    tmp_data["meta"]['version'] += f"- {speed}"  # 修改标题
    print(tmp_data["meta"]['version'])
    tmp_data["meta"]['time'] = int(time.time())  # 修改时间

    for i in range(len(json_data["time"])):  # 修改BPM
        tmp_data["time"][i]["bpm"] = speed * tmp_data["time"][i]["bpm"]

    tmp_data["note"][-1]["offset"] = int(tmp_data["note"][-1]["offset"] / speed)  # 修改偏移

    song_file = generate_song(speed, x, sr, outdir)

    tmp_data["note"][-1]["sound"] = song_file  # 设置歌曲文件

    outfile = f"{int(time.time())}-{speed}.mc"

    with open(os.path.join(outdir, outfile), "w") as f:
        json.dump(tmp_data, f)


def generate_beatmaps(outdir, json_data, speeds):
    sond_file = json_data["note"][-1]["sound"]
    x, sr = librosa.load(os.path.join(outdir, sond_file), sr=12000)

    for speed in speeds:
        speed = float(speed)
        generate_beatmap(json_data, x, sr, speed, outdir)

    tmp_name = get_tmp_dir() + ".mcz"
    tmp_path = os.path.join("upload_dir", tmp_name)

    file_dir = os.path.join("upload_dir", "tmp", get_tmp_dir())

    with zipfile.ZipFile(tmp_path, 'w') as f:
        for _dir in os.listdir(file_dir):
            _dir = os.path.join(file_dir, _dir)
            if os.path.isdir(_dir):
                for i in os.walk(_dir):
                    for n in i[2]:
                        f.write(os.path.join(i[0], n))

    return tmp_name
