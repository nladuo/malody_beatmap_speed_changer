
UPLOAD_DIR = ""


def get_file_extension(filename):
    if "." not in filename:
        return ""

    return filename.rsplit('.', 1)[1].lower()


def allowed_file(filename):
    ALLOWED_EXTENSIONS = [
        "mcz",
    ]
    return get_file_extension(filename) in ALLOWED_EXTENSIONS
