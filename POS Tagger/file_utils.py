import os


def ensure_dir(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
        except FileNotFoundError:
            print("Error: Could not create path" + path)
