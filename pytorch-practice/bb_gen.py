"""
TODO:
--Add label to top left of bbox
Resize images, make bbox coordinates relative (0, 1)
Ignore boxes that are obviously just a misclick
Change focus to toplevel automatically
Make bbox output JSON
Add button to move to next frame
"""

import tkinter
import imageio

from pathlib import Path
from tkinter import *
from PIL import ImageTk, Image
import json

video_path = Path("c:/users/john/desktop/ai-exploration/pytorch-practice/data/doom_gameplay.mp4")
bookmark_path = Path("frame_num.txt")
anno_path = Path("annotations.json")

if not bookmark_path.exists():
    with open(bookmark_path, "w") as f:
        f.write("0")

with open(bookmark_path) as f:
    frame_num = int(f.read())

if not anno_path.exists():
    with open(anno_path, "w") as f:
        f.write("[]")

annotations = json.load(open(anno_path))

frames = imageio.get_reader(video_path,  'ffmpeg')

AMMO = ["clip", "box of bullets", "shells", "box of shells",
        "rocket", "box of rockets", "small plasma", "big plasma"]

WEAPONS = ["chainsaw", "shotgun", "super shotgun", "chaingun",
           "rocket launcher", "plasma rifle", "bfg-9000"]

PICKUPS = ["health bonus", "stimpack", "medikit", "supercharge",
           "armor bonus", "armor", "mega-armor"]

POWERUPS = ["backpack", "berserk", "area map", "invulnerability",
            "night vision", "mega-sphere", "cloaking", "radiation suit"]

KEYS = ["red key", "blue key", "yellow key", "red skull key", "blue skull key",
        "yellow skull key"]

ENEMIES = ["baron of hell", "cacodemon", "cyberdemon", "pink demon", "imp",
           "lost soul", "shotgun guy", "specter", "spider mastermind",
           "zombieman", "arachnotron", "arch-vile", "heavy weapon dude",
           "hell knight", "mancubus", "pain elemental", "revenant"]

MISC = ["barrel", "fireball", "rocket projectile", "doomguy"]

start_pos = None
draw_start = None
canvas = None
rectangles = []
last_coord = None
last_class = None
img = None

def click(event):
    global start_pos
    start_pos = event.x, event.y

def release(event):
    global start_pos
    xs = sorted([start_pos[0], event.x])
    ys = sorted([start_pos[1], event.y])

    coords = (xs[0], ys[0], xs[1], ys[1])

    rectangles.append(coords)
    show_popup()
    start_pos = None

    global last_coord
    last_coord = coords

    draw_rectangles()

def drag(event):
    canvas.delete("all")
    draw_rectangles()
    canvas.create_rectangle(*start_pos, event.x, event.y, width = 2, outline = "red")

def draw_rectangles():
    draw_image()
    for rectangle in rectangles:
        canvas.create_rectangle(*rectangle, width = 2, outline = "yellow")

def draw_image():
    canvas.create_image(0, 0, image = img, anchor = "nw")

def show_popup():
    toplevel = Toplevel()
    label1 = Label(toplevel, text=", ".join(AMMO))
    label1.pack()

    entry1 = Entry(toplevel)
    entry1.pack()

    button1 = Button(toplevel, text = "Confirm", command = lambda: write_and_close(toplevel))
    button1.pack()

def write_and_close(toplevel):
    global last_class
    last_class = toplevel.winfo_children()[1].get()

    print("BB at {} contains {}".format(last_coord, last_class))
    d = {
    "label": last_class,
    "image_id": frame_num,
    "bbox": list(last_coord)
    }
    annotations.append(d)
    print(annotations)
    toplevel.destroy()
    write_label_to_bbox()

def write_label_to_bbox():
    lab = Label(canvas, text = last_class, fg = "yellow", bg = "black")
    lab.place(x = last_coord[0], y = last_coord[1])

def main():
    root = Tk()
    root.geometry("1200x675")
    root.title("testing123")

    global canvas
    canvas = Canvas(root)
    canvas.pack(fill = BOTH, expand = 1)

    data = frames.get_data(frame_num)
    raw = Image.fromarray(data, "RGB").resize((1200, 675))
    global img
    img = ImageTk.PhotoImage(raw)
    draw_image()

    canvas.bind("<Button-1>", click)
    canvas.bind("<ButtonRelease-1>", release)
    canvas.bind("<B1-Motion>", drag)

    root.mainloop()

if __name__ == "__main__":
    main()
