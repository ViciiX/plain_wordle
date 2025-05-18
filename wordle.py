import pandas as pd
import os, json, datetime
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk
import tkinter.ttk as ttk



def load_dict(path = os.getcwd()):
    return pd.read_pickle(os.path.join(path, "endict.pkl"))
    
endict = load_dict()
font_path = os.path.join(os.getcwd(), "wordle_font.ttf")

def get_target_word(word_length = None, tag = None):
	word = endict.loc[:,"word"]
	target_words = word
	if (word_length != None):
		length_mask = word.map(lambda x: len(x) == word_length)
		target_words = word.loc[length_mask]
	if (tag != None):
		tags = endict.loc[:,"tag"].loc[length_mask] if (word_length != None) else endict.loc[:,"tag"]
		tag_mask = tags.map(lambda x: bool(set([tag] if (type(tag) == str) else tag) & set(x.split(" "))) if (type(x) == str) else False)
		target_words = target_words.loc[tag_mask]
	return target_words.reset_index().loc[:, "word"]

def create_pane(letter, mode, img_size = 128):
	if (mode == "normal"):
		bg_color = "#FFFFFF"
		font_color = "#000000"
		border_color = "#787C7E"
	elif (mode == "correct"):
		bg_color = "#6AAA64"
		font_color = "#FFFFFF"
		border_color = bg_color
	elif (mode == "nearly"):
		bg_color = "#C9B458"
		font_color = "#FFFFFF"
		border_color = bg_color
	elif (mode == "incorrect"):
		bg_color = "#787C7E"
		font_color = "#FFFFFF"
		border_color = bg_color
	elif (mode == "empty"):
		bg_color = "#FFFFFF"
		font_color = "#FFFFFF"
		border_color = "#D3D6DA"
	img = Image.new("RGBA", (img_size, img_size), color = bg_color)
	font = ImageFont.truetype(font = font_path, size = 100 * (128//img_size))
	draw = ImageDraw.Draw(img)
	draw.rectangle(xy = [(0, 0), (img_size, img_size)], width = 5 * (128//img_size), outline = border_color)
	draw.text(xy = (img_size//2, img_size//2), text = letter, fill = font_color, font = font, anchor = "mm")
	return img

def get_word_img(word, answer, img_size = 128, horizontal_margin = 64, vertical_margin = 64, gap = 32):
	word = word.upper() + " " * (len(answer) - len(word))
	answer = answer.upper()
	word = word[0: len(answer)]
	img = Image.new("RGBA", (img_size * len(word) + gap * (len(word) - 1) + horizontal_margin * 2, img_size + vertical_margin * 2), color = "#FFFFFF")
	for i in range(len(word)):
		char = word[i]
		if (word[i] == answer[i]):
			mode = "correct"
		elif (word[i] in answer):
			mode = "nearly"
		elif (word[i] == " "):
			mode = "empty"
		else:
			mode = "incorrect"
		img.paste(create_pane(char, mode), (horizontal_margin + (img_size + gap) * i, vertical_margin))
	return img

def get_wordle_img(words, answer, length = 6, img_size = 128, horizontal_margin = 64, vertical_margin = 64, horizontal_gap = 32, vertical_gap = 32):
	words = [x.upper() for x in words]
	words += [" " * len(answer)] * (length - len(words))
	answer = answer.upper()
	img = Image.new("RGBA", (img_size * len(answer) + horizontal_gap * (len(answer) - 1) + horizontal_margin * 2, img_size * len(words) + vertical_gap * (len(words) - 1) + vertical_margin * 2), color = "#FFFFFF")
	for i in range(len(words)):
		word = words[i]
		paste_img = get_word_img(word, answer, img_size, 0, 0, horizontal_gap)
		img.paste(paste_img, (horizontal_margin, vertical_margin  + (img_size + vertical_gap) * i))
	return img


class ImageWidget():
	def __init__(self, root, image, **kwargs):
		self.source_img = image
		self.photo_img = ImageTk.PhotoImage(image)
		self.widget = ttk.Label(root, image = self.photo_img, **kwargs)
		self.widget.bind("<Configure>", self.resize)
		
	def pack(self, **kwargs):
		self.widget.pack(**kwargs)
	
	def grid(self, **kwargs):
		self.widget.grid(**kwargs)
	
	def resize(self, event):
		width = event.width
		height = event.height
		swidth, sheight = self.source_img.size
		scale = min(width/swidth, height/sheight)
		img = self.source_img.resize((round(swidth * scale), round(sheight * scale)))
		self.photo_img = ImageTk.PhotoImage(img)
		self.widget.config(image = self.photo_img)

class InputWidget():
	def __init__(self, root, hint = "", text_args = {}, entry_args = {}, text_pack_args = {}, entry_pack_args = {}):
		self.hint = hint
		self.frame = ttk.Frame(root)
		self.text_widget = ttk.Label(self.frame, text = hint, **text_args)
		self.entry_widget = ttk.Entry(self.frame, **entry_args, font = None)
		self.text_widget.pack(side = "left", **text_pack_args)
		self.entry_widget.pack(side = "right", **entry_pack_args)
	
	def pack(self, **kwargs):
		self.frame.pack(**kwargs)
	
	def grid(self, **kwargs):
		self.frame.grid(**kwargs)

class ComboboxWidget():
	def __init__(self, root, values):
		self.widget = ttk.Combobox(root, values = values)
		self.widget.current(0)
		self.value = tk.StringVar()
		
	def pack(self, **kwargs):
		self.widget.pack(**kwargs)
	
	def grid(self, **kwargs):
		self.widget.grid(**kwargs)

class App(tk.Tk):
	def __init__(self, size = 512):
		super().__init__()
		
		self.size = size
		
		self.grid_rowconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)
		self.grid_columnconfigure(0, weight=2)
		self.grid_columnconfigure(1, weight=1)
		
		self.style = ttk.Style()
		self.style.configure("a.TFrame", background = "blue")
		self.style.configure("b.TFrame", background = "red")
		
		self.img_area = ttk.Frame(self, style = "a.TFrame")
		self.create_area = ttk.Frame(self,style= "b.TFrame")
		self.reply_area = ttk.Frame(self)
		
		self.img_area.grid(sticky = "nwse", column = 0, row = 0, rowspan = 2)
		self.create_area.grid(sticky = "nwse", column = 1, row = 0)
		self.reply_area.grid(sticky = "nwse", column = 1, row = 1)
		
		self.img_area.pack_propagate(0)
		self.create_area.pack_propagate(0)
		self.reply_area.pack_propagate(0)
		
		ImageWidget(self.img_area, get_wordle_img(["hello,","world!","this is","a wordle","game by","Python"], "abcdefaaaaaaaaaaaagh")).pack(fill=tk.BOTH, expand=True)
		InputWidget(self.create_area, "test").pack(fill=tk.BOTH)
		ComboboxWidget(self.create_area, ["test1", "test2"]).pack(fill=tk.BOTH)
		
		self.geometry(f"{size//2*3}x{size}")
		self.mainloop()

app = App()