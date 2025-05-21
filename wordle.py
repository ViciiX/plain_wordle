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

def add_update(opt, target):
	opt.update(target)
	return opt

class ImageWidget():
	def __init__(self, root, image, **kwargs):
		self.root = root
		self.source_img = image
		self.photo_img = ImageTk.PhotoImage(self.source_img)
		self.widget = ttk.Label(root, image = self.photo_img, **kwargs)
		self.widget.bind("<Configure>", self.on_resize)
		
	def pack(self, **kwargs):
		kwargs = add_update({"fill": "both", "expand": True}, kwargs)
		self.widget.pack(**kwargs)
	
	def grid(self, **kwargs):
		self.widget.grid(**kwargs)
	
	def set_image(self, img):
		self.photo_img = ImageTk.PhotoImage(img)
		self.widget.config(image = self.photo_img)
	
	def replace_image(self, img):
		self.source_img = img
		self.on_resize()
	
	def on_resize(self, event = None):
		width = self.root.winfo_width()
		height = self.root.winfo_height()
		swidth, sheight = self.source_img.size
		scale = min(width/swidth, height/sheight)
		img = self.source_img.resize((round(swidth * scale), round(sheight * scale)))
		self.set_image(img)

class TextBaseWidget():
	def __init__(self, root, bind_widgets = None, font_name = "微软雅黑", font_size = 12):
		self.root = root
		self.origin_size = None
		self.font = (font_name, font_size)
		if (bind_widgets != None):
			self.bind_resize(bind_widgets)
		
	def bind_resize(self, widgets):
		if (type(widgets) != list):
			widgets.bind("<Configure>", self.on_resize)
		else:
			for widget in widgets:
				widget.bind("<Configure>", self.on_resize)
		
	def on_resize(self, event):
		event.width, event.height = self.root.winfo_width(), self.root.winfo_height()
		if (self.origin_size == None):
			self.origin_size = (event.width, event.height)
		width, height = event.width, event.height
		rwidth, rheight = self.origin_size
		scale = min(width/rwidth, height/rheight)
		event.widget.configure(font = (self.font[0], round(self.font[1] * scale)))
	
	def pack(self, **kwargs):
		kwargs = add_update({"fill": "x"}, kwargs)
		self.widget.pack(**kwargs)
	
	def grid(self, **kwargs):
		self.widget.grid(**kwargs)
	
class LabelWidget(TextBaseWidget):
	def __init__(self, root, text, font_name = "微软雅黑", font_size = 12, **kwargs):
		kwargs = add_update({"anchor": "center"}, kwargs)
		self.widget = ttk.Label(root, text = text, **kwargs)
		super().__init__(root, self.widget, font_name, font_size)

class ButtonWidget(TextBaseWidget):
	def __init__(self, root, text, func, font_name = "微软雅黑", font_size = 12, **kwargs):
		self.widget = tk.Button(root, text = text, command = func, **kwargs)
		super().__init__(root, self.widget, font_name, font_size)
	
class HintInputWidget(TextBaseWidget):
	def __init__(self, root, widget_class, hint = "", text_position = "left", font_name = "微软雅黑", font_size = 12, text_args = {}, text_pack_args = {}, widget_args = {}, widget_pack_args = {}):
		super().__init__(root, font_name = font_name, font_size = font_size)
		self.hint = hint
		self.frame = ttk.Frame(root)
		self.side = text_position
		
		text_args = add_update({"text": hint, "anchor": "center", "font": self.font}, text_args)
		self.text_widget = ttk.Label(self.frame, **text_args)
		text_pack_args = add_update({"side": self.side, "fill": "both", "expand": True, "anchor": "nw"}, text_pack_args)
		self.text_widget.pack(**text_pack_args)
		
		self.input_widget = widget_class(self.frame, **widget_args)
		widget_pack_args = add_update({"fill": "both", "expand": True, "anchor": "nw", "side": {"left": "right", "top":"bottom", "right": "left", "bottom": "top"}[text_position]}, widget_pack_args)
		self.input_widget.pack(**widget_pack_args)
		
		self.frame.bind("<Configure>", self.on_text_resize)
	
	def on_text_resize(self, event):
		event.width, event.height = self.root.winfo_width(), self.root.winfo_height()
		if (self.origin_size == None):
			self.origin_size = (event.width, event.height)
		width, height = event.width, event.height
		rwidth, rheight = self.origin_size
		scale = min(width/rwidth, height/rheight)
		self.text_widget.configure(font = (self.font[0], round(self.font[1] * scale)))
		self.input_widget.configure(font = (self.font[0], round(self.font[1] * scale)))

class EntryWidget(HintInputWidget):
	def __init__(self, root, hint, **kwargs):
		self.value = tk.StringVar()
		widget_args = kwargs.get("widget_args", {})
		kwargs["widget_args"] = add_update({"textvariable": self.value}, widget_args)
		kwargs = add_update({"hint": hint}, kwargs)
		super().__init__(root, ttk.Entry, **kwargs)
	
	def pack(self, **kwargs):
		if (self.side in ["left", "right"]):
			fill = "both"
		else:
			fill = "x"
		kwargs = add_update({"fill": fill}, kwargs)
		self.frame.pack(**kwargs)

class OptionWidget(HintInputWidget):
	def __init__(self, root, values, hint, select_handle = None, **kwargs):
		self.value = tk.StringVar()
		self.select_handle = select_handle
		widget_args = kwargs.get("widget_args", {})
		kwargs["widget_args"] = add_update({"textvariable": self.value, "values": values, "justify": "center", "state": "readonly", "exportselection": False}, widget_args)
		kwargs = add_update({"hint": hint}, kwargs)
		
		super().__init__(root, ttk.Combobox, **kwargs)
		self.input_widget.current(0)
		self.input_widget.bind('<<ComboboxSelected>>', self.on_selected)
		
	def pack(self, **kwargs):
		kwargs = add_update({"fill": "x"}, kwargs)
		self.frame.pack(**kwargs)
		
	def on_selected(self, event):
		event.widget.master.focus() #消除选择后的蓝色高亮
		if (self.select_handle != None):
			self.select_handle(self.value.get())

class App(tk.Tk):
	def __init__(self, size = 512):
		super().__init__()
		
		self.size = size
		self.tag = ""
		self.length = ""
		
		self.img_area = ttk.Frame(self)
		self.create_area = ttk.Frame(self)
		self.reply_area = ttk.Frame(self)
		
		self.hint_widget = None
		self.image_widget = ImageWidget(self.img_area, get_wordle_img(["empty", " mpty", " m ty", " m t "], "empty"))
		self.image_widget.pack()
		
		self.grid_rowconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)
		self.grid_columnconfigure(0, weight=2)
		self.grid_columnconfigure(1, weight=1)
		
		self.img_area.grid(sticky = "nwse", column = 0, row = 0, rowspan = 2)
		self.create_area.grid(sticky = "nwse", column = 1, row = 0)
		self.reply_area.grid(sticky = "nwse", column = 1, row = 1)
		
		self.img_area.pack_propagate(0)
		self.create_area.pack_propagate(0)
		self.reply_area.pack_propagate(0)
		
		self.add_create_area_widgets()

		self.geometry(f"{size//2*3}x{size}")
		self.mainloop()
	
	def add_create_area_widgets(self):
		def pressed():
			length = self.length.get()
			tag = {"中考": "zk", "高考": "gk", "任意": None}[self.tag.get()]
			if (length.isdigit() or length == ""):
			   if (length == "" or (4 <= int(length) and int(length) <= 15)):
				   length = int(length) if (length != "") else None
				   self.create_wordle(length, tag)
			   else:
				   self.hint("只支持4-15长度的单词")
			else:
				self.hint("长度一栏请输入4-15的数字！")
		
		length_widget = EntryWidget(self.create_area, "单词长度")
		option_widget = OptionWidget(self.create_area, ["任意", "中考", "高考"], "选择标签")
		button_widget = ButtonWidget(self.create_area, "创建", pressed)
		self.hint_widget = LabelWidget(self.create_area, "")
		
		self.length = length_widget.value
		self.tag = option_widget.value
		
		length_widget.pack()
		option_widget.pack()
		button_widget.pack()
		self.hint_widget.pack()
	
	def hint(self, text, time = 3):
		self.hint_widget.widget.configure(text = text)
		if (time != None):
			self.hint_widget.widget.after(time * 1000, self.hint, "", None)
	
	def create_wordle(self, length, tag):
		if (length == None):
			word = endict.loc[:, "word"]
		else:
			word = get_target_word(int(length), tag)
		if (word.empty == False):
			self.word = word.sample().values[0]
			self.info = json.loads(endict.loc[endict.loc[:, "word"] == self.word].reset_index().to_json())
			self.image_widget.replace_image(get_wordle_img([], self.word))
			self.hint("创建成功！")
		else:
			self.hint("单词数据库内未找到单词")
	
app = App()