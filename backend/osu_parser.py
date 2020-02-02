"""
    OSU谱面文件解析器
    参考：https://osu.ppy.sh/help/wiki/osu!_File_Formats/Osu_(file_format)
"""


class OsuFileParser:
    @staticmethod
    def read_osu_file(filepath):
        obj = {}
        key_pair_sections = ["General", "Editor", "Metadata", "Difficulty", "Colours"]
        with open(filepath, "r", encoding="utf-8") as f:
            file_format = f.readline()
            obj["format"] = file_format.strip()
            section = ""  # 当前的section
            for line in f.readlines():
                line = line.strip()
                # print(line)
                if line.startswith("//") or line.startswith("#"):
                    continue

                if line.startswith("[") and line.endswith("]"):
                    section = line.replace("[", "").replace("]", "")
                    if section in key_pair_sections:  # 如果是键值对类型
                        obj[section] = {}
                    else:                             # 如果是Comma-separated lists
                        obj[section] = []
                    # print(section)
                elif line != "":
                    if section in key_pair_sections:  # 如果是键值对类型
                        splits = line.split(":")
                        # print(splits)
                        k = splits[0].strip()
                        v = splits[1].strip()
                        obj[section][k] = v
                    else:                             # 如果是Comma-separated lists
                        obj[section].append(line)

        return obj



    @staticmethod
    def write_osu_file(obj, outfilepath):
        output_order = [
            "General",
            "Editor",
            "Metadata",
            "Difficulty",
            "Events",
            "TimingPoints",
            "Colours",
            "HitObjects",
        ]
        key_pair_sections = ["General", "Editor", "Metadata", "Difficulty", "Colours"]

        result = obj["format"]

        for section in output_order:
            if section not in obj:
                continue
            result += f"\n\n[{section}]"
            if section in key_pair_sections:
                for k in obj[section].keys():
                    result += f"\n{k}: {obj[section][k]}"
            else:
                for line in obj[section]:
                    result += f"\n{line}"

        result += "\n"

        with open(outfilepath, "w") as f:
            f.write(result)
