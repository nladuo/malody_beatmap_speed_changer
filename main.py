from flask import Flask, send_from_directory, request
import json
import os
from backend.beatmap_helper import *
from backend.utils import *
import traceback


app = Flask(__name__, static_folder='dist')


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('./dist/static', path)


@app.route('/api/get_file/<path:path>')
def serve_get_file(path):
    return send_from_directory('./upload_dir', path)


@app.route('/api/get_speeds')
def api_get_speeds():
    speeds = []
    try:
        with open("speeds.txt", "r") as f:
            for line in f.readlines():
                try:
                    speed = int(1000 * float(line)) / 1000
                    if (speed > 0.49999) and (speed < 2.00001):
                        speeds.append(speed)
                except:
                    pass
    except:
        pass

    if len(speeds) == 0:
        speeds = [0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.4, 1.5, 1.6, 1.7, 2.0]

    return json.dumps({
        "success": True,
        "speeds": speeds
    })

@app.route('/api/upload_file', methods=["POST"])
def api_upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return json.dumps({'success': False, 'msg': '请求参数错误'})
        file = request.files['file']
        if file.filename == '':
            return json.dumps({'success': False, 'msg': '没选择文件'})
        else:
            if file and allowed_file(file.filename):
                origin_file_name = file.filename
                print(origin_file_name)
                file.save(os.path.join("upload_dir", "tmp", origin_file_name))
                with open(os.path.join("upload_dir", "now_file.txt"), "w") as ft:
                    ft.write(origin_file_name)

                beatmaps = get_beatmaps(create=True)

                if len(beatmaps) != 0:
                    return json.dumps({'success': True, 'beatmaps': beatmaps, 'msg': '成功'})
                else:
                    return json.dumps({'success': False, 'msg': '未找到谱面'})

            else:
                return json.dumps({'success': False, 'msg': '文件类型错误，请上传mcz格式'})


@app.route('/api/generate_beatmaps')
def api_generate_beatmaps():
    try:
        speeds = request.args.get("speeds")
        index = request.args.get("index")
        index = int(index)
        speeds = json.loads(speeds)

        beatmaps = get_beatmaps(create=False)
        beatmap = beatmaps[index]
        outdir = beatmap["out_dir"]
        json_data = beatmap["json_data"]
        tmp_file = generate_beatmaps(outdir, json_data, speeds)
        return json.dumps({
            "success": True,
            "file": tmp_file
        })
    except:
        traceback.print_exc()
        return json.dumps({
            "success": False
        })


if __name__ == '__main__':
    app.run(port=4776, debug=True)
