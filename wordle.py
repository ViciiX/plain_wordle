import pandas as pd
import os, json, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk
import tkinter.ttk as ttk

if (hasattr(sys, "_MEIPASS")):
	data_path = os.path.join(sys._MEIPASS, "data")
else:
	data_path = os.path.join(os.getcwd(), "data")

def load_dict():
	if (sys.maxsize > 2**32):
		return pd.read_pickle(os.path.join(data_path, "endict.pkl"))
	else:
		return pd.read_pickle(os.path.join(data_path, "endict32.pkl"))

endict = load_dict()
font_path = os.path.join(data_path, "wordle_font.ttf")
tags = {"任意": None, "中考": "zk", "高考": "gk", "四级": "cet4", "六级": "cet6", "托福": "toefl", "GRE": "gre"}

def get_target_word(word_length = None, word_tag = None, word_frq = None):
	length_cond = (((word_length == None) & (endict.loc[:,"word"].str.len() >= 4)) | (endict.loc[:,"word"].str.len() == word_length))
	frq_cond = ((word_frq == None) | (endict.loc[:,"frq"] <= word_frq))
	data = endict.loc[length_cond & frq_cond]
	def isin(x):
		if (word_tag == None):
			return True
		if (pd.isna(x) == False):
			tags = set(x.split(" "))
			filters = set([word_tag]) if (type(word_tag) == str) else set(word_tag)
			return filters.issubset(tags)
		else:
			return False
	data = data.loc[data.loc[:, "tag"].map(lambda x: isin(x))]
	return data.loc[:, "word"]

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
		self.widget = tk.Label(root, text = text, **kwargs)
		super().__init__(root, self.widget, font_name, font_size)

class MessageWidget(TextBaseWidget):
	def __init__(self, root, text, font_name = "微软雅黑", font_size = 12, **kwargs):
		kwargs = add_update({"anchor": "center"}, kwargs)
		self.widget = tk.Message(root, text = text, **kwargs)
		super().__init__(root, self.widget, font_name, font_size)
	
	def on_resize(self, event):
		swidth, sheight = event.width, event.height
		width, height = self.root.winfo_width(), self.root.winfo_height()
		if (self.origin_size == None):
			self.origin_size = (width, height)
		
		rwidth, rheight = self.origin_size
		scale = min(width/rwidth, height/rheight)
		self.widget.configure(font = (self.font[0], round(self.font[1] * scale)), aspect = round(swidth/sheight * 100))


class ButtonWidget(TextBaseWidget):
	def __init__(self, root, text, func, font_name = "微软雅黑", font_size = 12, **kwargs):
		self.widget = tk.Button(root, text = text, command = lambda: func(self.widget), **kwargs)
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
	def __init__(self, root, hint, placeholder = None, **kwargs):
		self.value = tk.StringVar()
		self.placeholder = placeholder
		widget_args = kwargs.get("widget_args", {})
		kwargs["widget_args"] = add_update({"textvariable": self.value}, widget_args)
		kwargs = add_update({"hint": hint}, kwargs)
		super().__init__(root, tk.Entry, **kwargs)
		self.input_widget.bind("<FocusIn>", self.focusin)
		self.input_widget.bind("<FocusOut>", self.focusout)
		self.focusout()
		
	def pack(self, **kwargs):
		if (self.side in ["left", "right"]):
			fill = "both"
		else:
			fill = "x"
		kwargs = add_update({"fill": fill}, kwargs)
		self.frame.pack(**kwargs)
	
	def disable(self):
		self.input_widget.configure(state = "disabled")
	
	def enable(self):
		self.input_widget.configure(state = "normal")
	
	def focusin(self, event = None):
		if (self.placeholder != None and self.value.get() == self.placeholder):
			self.clear()
			self.input_widget.configure(fg = "#000000")
			self.input_widget.configure(justify = "left")
	
	def focusout(self, event = None):
		if (self.placeholder != None and self.value.get() == ""):
			self.input_widget.insert(0, self.placeholder)
			self.input_widget.configure(fg = "#BBBBBB")
			self.input_widget.configure(justify = "center")
	
	def clear(self):
		self.input_widget.delete(0, len(self.value.get()))

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
		self.frq = ""
		self.length = ""
		self.word = ""
		self.words = []
		self.tips = []
		self.answer = ""
		
		self.img_area = ttk.Frame(self, relief = "groove", padding = 5)
		self.create_area = ttk.Frame(self, relief = "groove", padding = 5)
		self.reply_area = ttk.Frame(self, relief = "groove", padding = 5)
		self.info_area = ttk.Frame(self, relief = "groove", padding = 5)
		
		self.image_widget = ImageWidget(self.img_area, get_wordle_img(["empty", " mpty", " m ty", " m t "], "empty"))
		self.answer_widget = None
		self.image_widget.pack()
		
		self.grid_rowconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)
		self.grid_columnconfigure(0, weight=2)
		self.grid_columnconfigure(1, weight=1)
		self.grid_columnconfigure(2, weight=1)

		
		self.img_area.grid(sticky = "nwse", column = 0, row = 0, rowspan = 2)
		self.create_area.grid(sticky = "nwse", column = 1, row = 0)
		self.reply_area.grid(sticky = "nwse", column = 1, row = 1)
		self.info_area.grid(sticky = "nwse", column = 2, row = 0 ,rowspan = 2)
		
		self.img_area.pack_propagate(0)
		self.create_area.pack_propagate(0)
		self.reply_area.pack_propagate(0)
		self.info_area.pack_propagate(0)
		
		self.add_create_area_widgets()
		self.add_reply_area_widgets()

		self.geometry(f"{size*2}x{size}")
		self.title("Plain Wordle")
		self.iconbitmap(os.path.join(data_path, "icon.ico"))
		self.mainloop()
	
	def add_create_area_widgets(self):
		hint_widget = LabelWidget(self.create_area, "")
		
		def hint(text, time = 2):
			self.hint(hint_widget.widget, text, time)
			
		def pressed(widget):
			length = self.length.get()
			if (length.isdigit() or length == "" or length == "留空为任意"):
			   if (length == "" or length == "留空为任意" or (4 <= int(length) and int(length) <= 15)):
				   length = int(length) if (length != "" and length != "留空为任意") else None
				   tag = tags[self.tag.get()]
				   frq = None if (self.frq.get() == "任意") else int(self.frq.get()[1:])
				   self.create_wordle(hint_widget.widget, length, tag, frq)
				   widget.configure(state = "disabled")
				   widget.after(1000, widget.configure, {"state": "active"})
			   else:
				   hint("只支持4-15长度的单词")
			else:
				hint("长度一栏请输入4-15的数字！")
		
		length_widget = EntryWidget(self.create_area, "单词长度", "留空为任意")
		tag_widget = OptionWidget(self.create_area, list(tags.keys()), "选择标签")
		frq_widget = OptionWidget(self.create_area, ["任意", "前100", "前1000", "前3000", "前5000", "前10000", "前20000", "前30000"], "词频")
		button_widget = ButtonWidget(self.create_area, "创建", pressed)
		
		self.length = length_widget.value
		self.tag = tag_widget.value
		self.frq = frq_widget.value
		
		length_widget.pack()
		tag_widget.pack()
		frq_widget.pack()
		button_widget.pack()
		hint_widget.pack()
	
	def add_reply_area_widgets(self):
		hint_widget = LabelWidget(self.reply_area, "")
		
		def hint(text, time = 2):
			self.hint(hint_widget.widget, text, time)
		
		def show_info(word):
			info = json.loads(endict.loc[endict.loc[:, "word"] == word].reset_index().to_json())
			translation = info.get("translation", {}).get("0", "未找到").replace("\\n", "\n")
			word_tags = info.get("tag", {}).get("0", None)
			if (word_tags != None):
				tag_text = word_tags.replace(" ", "; ")
			else:
				tag_text = "无"
			info_str = "答案：\n" if (word == self.word) else ""
			info_str += f"""单词：{word}
音标：[{info.get("phonetic", {}).get("0", "未找到")}]
中文释义：
{translation}
词频排名：{info.get("frq", {}).get("0", "未找到")}
标签：{tag_text}"""
			self.hint(info_widget.widget, info_str ,None)
		
		def on_answer(event):			
			answer = self.answer.get().lower()
			if (len(answer) == len(self.word)):
				if (endict.loc[endict.loc[:, "word"] == answer].empty == False):
					info_widget.widget.configure(bg = "#fb6f6f")
					
					show_info(answer)
					if (answer == self.word):
						hint("恭喜你猜对了！")
						show_ans(None, "#7defc1")
					elif (len(self.words) == 5):
						hint("次数用尽，再接再厉！")
						show_ans(None, "#ef7d7d")
					else:
						self.words.append(answer)
						self.update_wordle_img()
				else:
					hint("单词数据库内未找到单词\n- 试试用原型？")
			else:
				hint("单词长度不一致！")
			self.answer_widget.clear()

		def tip(event):
			if (len(self.tips) > 0 and self.word not in self.words):
				if (len(self.words) < 5 and len(self.tips) > 1):
					tip_word = ["?"] * len(self.word)
					del self.tips[random.randint(0, len(self.tips) - 1)]
					for i in range(len(self.word)):
						if (i not in self.tips):
							tip_word[i] = list(self.word)[i]
					self.words.append("".join(tip_word))
					self.update_wordle_img()
				else:
					hint("要不你还是揭晓答案吧")
			else:
				hint("没什么好提示的啦")
		
		def show_ans(event = None, bg = None):
			if (self.word not in self.words and self.word != ""):
				info_widget.widget.configure(bg = bg)
				self.words.append(self.word)
				show_info(self.word)
				self.answer_widget.disable()
				self.update_wordle_img()

		self.answer_widget = EntryWidget(self.reply_area, "输入单词")
		self.answer_widget.disable()
		self.answer_widget.input_widget.bind("<Return>", on_answer)
		
		tip_widget = ButtonWidget(self.reply_area, "提示", tip)
		showans_widget = ButtonWidget(self.reply_area, "揭晓答案", lambda x: show_ans(x, "#7defc1"))
		
		info_widget = MessageWidget(self.info_area, "",  anchor = "nw", justify = "left")
		itsme = LabelWidget(self.info_area, "ViciiX", font_size = 8, fg = "#BBBBBB", anchor = "se")
		
		self.answer_widget.pack()
		tip_widget.pack()
		showans_widget.pack()
		hint_widget.pack()
		info_widget.pack()
		itsme.pack(fill = "both", expand = True, anchor = "se")
		
		self.answer = self.answer_widget.value
	
	def hint(self, widget, text, time = 2):
		widget.configure(text = text)
		if (time != None):
			widget.after(time * 1000, self.hint, widget, "", None)
	
	def create_wordle(self, hint_widget, length, tag, frq):
		word = get_target_word(length, tag, frq)
		if (word.empty == False):
			self.words = []
			self.answer_widget.enable()
			self.word = word.sample().values[0]
			self.tips = list(range(len(self.word)))
			self.update_wordle_img()
			self.hint(hint_widget, "创建成功！", 1)
			print(self.word)
		else:
			self.hint(hint_widget, "单词数据库内未找到单词")
	
	def update_wordle_img(self):
		self.image_widget.replace_image(get_wordle_img(self.words, self.word))
app = App()