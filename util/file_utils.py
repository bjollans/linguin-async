import os
import requests

def download_image_from_url(url, filename):
    r = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(r.content)

def file_exists(filename):
    return os.path.isfile(filename)
