import glob
import os
from wand.image import Image, Color
from pathlib import Path

root_dir = "../"


def resize_and_save_as_dds(png_image: str, open_image: Image, index):
    print(f"Converting {png_image} to .dds from .png")
    path = Path(png_image)
    with Image(width=1024, height=1024, background=Color("transparent")) as bg:
        open_image.resize(600, 800)
        bg.composite(open_image, left=234, top=-15)
        bg.compression = "dxt5"
        head_tail = os.path.split(path)
        head = head_tail[0]
        splithead = head.split("\\")
        filepath = head_tail[0] + "\\" + splithead[-1].lower() + "_" + splithead[-2].lower() + "_" +  str(index) + ".dds"
        bg.save(filename=filepath)

print(root_dir + "gfx/models/skins/skins_textures/body/Bears/**/*.png")
id = 0
for png_image in glob.iglob(
   "gfx/models/skins/skins_textures/body/**/*.png", recursive=True
):
    with Image(filename=png_image) as open_image:
        id = id + 1
        resize_and_save_as_dds(png_image, open_image, id)
