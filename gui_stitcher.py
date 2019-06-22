import tkinter as tk
from tkinter import filedialog
from panorama import Stitcher
from video_reader import frame_generator
import cv2


root = tk.Tk()
root.title("HyperMapStitcher")
root.wm_iconbitmap("hms.ico")
stitcher = Stitcher()

frame = tk.Frame(root, width=300, height=250, padx=15, pady=15)

input_filename = ""
input_hint_label = tk.Label(frame, text="Must specify an input file")

output_filename = ""
output_hint_label = tk.Label(frame, text="Must specify an output file")

manual_checkbox = tk.IntVar()


def input_file():
    global input_filename
    input_filename = filedialog.askopenfilename(initialdir=".", title="Select input video",
                                                filetypes=[["video files", ["*.mp4", "*.avi"]], ["all files", "*.*"]])


def output_file():
    global output_filename
    output_filename = filedialog.asksaveasfilename(initialdir=".", title="Select output filename", initialfile="out.png")


def call_stitch():

    input_hint_label.pack_forget()
    output_hint_label.pack_forget()

    frames = int(frame_entry.get())
    width = int(width_entry.get())
    manual = bool(manual_checkbox.get())

    if input_filename == "":
        input_hint_label.pack()
    else:
        print(input_filename)

    if output_filename == "":
        output_hint_label.pack()
    else:
        print(output_filename)

    if (input_filename != "") & (output_filename != ""):
        images = frame_generator(input_filename, frames=frames, width=width)
        result = stitcher.multistitch(images, manual=manual, os="win")
        cv2.imwrite(output_filename, result)
        root.destroy()


tk.Label(frame, text="Frame count").pack()
frame_entry = tk.Entry(frame)
frame_entry.insert(0, "10")
frame_entry.pack()

tk.Label(frame, text="Scale to width").pack()
width_entry = tk.Entry(frame)
width_entry.insert(0, "477")
width_entry.pack()

tk.Checkbutton(frame, text="Manual mode?", variable=manual_checkbox).pack()

tk.Button(frame, text="Input file", command=input_file, width=10).pack()
tk.Button(frame, text="Output file", command=output_file, width=10).pack()

tk.Button(frame, text="Stitch!", command=call_stitch, width=10).pack()

frame.pack(expand=True, fill='both')
frame.pack_propagate(0)
root.mainloop()
