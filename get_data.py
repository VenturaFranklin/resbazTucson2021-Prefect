import os
import gdown
from pathlib import Path

os.chdir(Path(__file__).parent / "data")

with open("files_gdrive.txt", "r") as fileio:
    files = fileio.readlines()

for url in files:
    url = url.rstrip("\n")
    gdown.download(url)
