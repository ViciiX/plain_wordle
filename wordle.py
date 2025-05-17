import pandas as pd
import os, json
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk



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
	word = word.upper()
	answer = answer.upper()
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

def get_wordle_img(words, answer, img_size = 128, horizontal_margin = 64, vertical_margin = 64, horizontal_gap = 32, vertical_gap = 32):
	words = [x.upper() for x in words]
	words += [" " * len(answer)] * (6 - len(words))
	answer = answer.upper()
	img = Image.new("RGBA", (img_size * len(answer) + horizontal_gap * (len(answer) - 1) + horizontal_margin * 2, img_size * len(words) + vertical_gap * (len(words) - 1) + vertical_margin * 2), color = "#FFFFFF")
	for i in range(len(words)):
		word = words[i]
		paste_img = get_word_img(word, answer, img_size, 0, 0, horizontal_gap)
		img.paste(paste_img, (horizontal_margin, vertical_margin  + (img_size + vertical_gap) * i))
	return img


class ImageWidget():
	def __init__(self, root, image, **kwargs):
		super().__init__()
		self.source_img = image
		self.photo_img = ImageTk.PhotoImage(image)
		self.widget = tk.Label(root, image = self.photo_img, **kwargs)
		
	def pack(self, **kwargs):
		self.widget.pack()

class App(tk.Tk):
	def __init__(self):
		super().__init__()
		img = ImageWidget(self, get_wordle_img([], "test"))
		self.mainloop()

app = App()
