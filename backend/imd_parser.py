"""
    节奏大师谱面文件解析器,
    参考rmstZ的html代码
"""
import struct

class ImdFileParser:
    @staticmethod
    def read_imd_file(filepath):
        version = filepath.split("/")[-1].split('\\')[-1].replace(".imd", "")
        obj = {
            "version": version,
            "song_file": version.split("_")[0].split("-")[0].split(".")[0]+".mp3",
            "song_name": version.split("_")[0].split("-")[0].split(".")[0]
        }
        try:
            f = open(filepath, 'rb')

            f.seek(0, 0)

            length = struct.unpack('i', f.read(4))[0]
            print(length)
            obj["length"] = length

            count = struct.unpack('i', f.read(4))[0]
            print(count)
            obj["count"] = count

            bpm_list = []
            for i in range(count):
                t = struct.unpack('i', f.read(4))[0]
                bpm = struct.unpack('d', f.read(8))[0]
                bpm_list.append({
                    "t": t,
                    "bpm": bpm
                })
            obj["bpm_list"] = bpm_list

            flag = struct.unpack('h', f.read(2))[0]
            count2 = struct.unpack('i', f.read(4))[0]

            obj["flag"] = flag
            obj["count2"] = count2

            print(flag, count2)
            notes = []
            for i in range(count2):
                action = struct.unpack('h', f.read(2))[0]
                time = struct.unpack('i', f.read(4))[0]
                track = struct.unpack('b', f.read(1))[0]
                param = struct.unpack('i', f.read(4))[0]

                notes.append({
                    "action": action,
                    "time": time,
                    "track": track,
                    "param": param,
                })

            obj["notes"] = notes
            print("final-->", f.read())
            print(notes)
            f.close()
        except:
            pass
        return obj


    @staticmethod
    def write_imd_file(obj, outfilepath):
        f = open(outfilepath, "wb")
        f.write(struct.pack('i', obj["length"]))
        f.write(struct.pack('i', obj["count"]))

        for bpm in obj["bpm_list"]:
            f.write(struct.pack('i', bpm["t"]))
            f.write(struct.pack('d', bpm["bpm"]))

        f.write(struct.pack('h', obj["flag"]))
        f.write(struct.pack('i', obj["count2"]))

        for note in obj["notes"]:
            f.write(struct.pack('h', note["action"]))
            f.write(struct.pack('i', note["time"]))
            f.write(struct.pack('b', note["track"]))
            f.write(struct.pack('i', note["param"]))

        f.close()
