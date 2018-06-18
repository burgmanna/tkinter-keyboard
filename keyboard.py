'''Popup Keyboard is a module to be used with Python's Tkinter library
It subclasses the Entry widget as KeyboardEntry to make a fullscreen pop-up
keyboard appear as the widget gains focus. Development in progress and focused to use with small touchscreens.
'''

from tkinter import *
import math
import abc
import inspect

class _PopupKeyboard(Toplevel):
	'''A Toplevel instance that displays a keyboard that is attached to
	another widget. Only the Entry widget has a subclass in this version.
	'''
	
	def __init__(self, parent, attach, buttonsettings, entrysettings, validator):
		Toplevel.__init__(self, takefocus=0)

		self.overrideredirect(True)
		self.attributes('-alpha',0.95)
		self.parent = parent
		self.attach = attach
		self.keyframe = Frame(self)
		self.toprow = Frame(self.keyframe)

		self.delete = '←'
		#append 0 to this array to get placed on right side later
		nums = [i for i in range(1,10)]
		nums.append(0)
		#define key layout
		self.keys = [
			nums,
			['q', 'w', 'e', 'r', 't', 'z', 'u', 'i', 'o', 'p', '/', self.delete],
			['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l',','],
			['shift','y', 'x', 'c', 'v', 'b', 'n', 'm','.','?'],
			['@','#','%','*','[ space ]','+','-','=', 'submit']
			]
		self.keyframe.pack()
		self.toprow.grid(row=1)
		self.rows = {}
		for	i in range(len(self.keys)):
			self.rows[i] = Frame(self.keyframe)
			self.rows[i].grid(row=i+2)
		
		if validator and isinstance(validator, InputValidator):
			self.validator = validator
		else:
			self.validator = None
		self.keycount = max([len(n) for n in self.keys])
		ks = math.floor(self.winfo_width() / self.keycount)
		if not "width" in buttonsettings or buttonsettings["width"] > ks:
			buttonsettings["width"] = ks
		spw = self.parent.winfo_screenwidth() - self.winfo_reqwidth() #calulate space to the sides
		if spw > 0:
			self.x = math.floor(spw/2) #center keyboard
		sph = self.parent.winfo_screenheight() - self.winfo_reqheight()
		if sph > 0:
			self.y = math.floor(sph/2)
		self.keyframe.place(x=0,y=self.y)
		self.buttonsettings = buttonsettings
		self.entrysettings = entrysettings
		self._init_keys()

		self.update_idletasks()
		self.geometry('{}x{}+{}+{}'.format(self.parent.winfo_screenwidth(),
										   self.parent.winfo_screenheight(),
										   0, 0))
		#self.mainframe.geometry('{}x{}+{}+{}'.format(self.winfo_width(),self.winfo_height(),self.x,self.y))
		#self.bind('<FocusOut>', lambda e: self._check_kb_state('focusout'))
		self.bind('<Return>', lambda e: self._check_kb_state('return'))
		
	def _check_kb_state(self, event):
		if (event == 'focusout' and not (self.focus_get() == self or self.parent.focus_get() == self.parent)) or event == 'return':
			self.parent._destroy_popup()

	def _init_keys(self):
		self.entryfield = Entry(self.toprow, **self.entrysettings)
		self.entryfield.pack(anchor=CENTER)
		self.entryfield.insert(END,self.attach.get())
		self.entryfield.focus_set()
		i = 0
		for row in self.keys:
			for key in row:
				multiplier = 1
				b = Button(self.rows[i], text=key, **self.buttonsettings)
				b.bind("<ButtonRelease-1>", self._attach_key_press)
				b.grid(row=0, column=row.index(key))
			i = i+1

	def _destroy_popup(self):
		self.destroy()

	def _attach_key_press(self, btn):
		k = btn.widget['text']
		if k == self.delete:
			self.entryfield.delete(self.entryfield.index(INSERT)-1, INSERT)
		elif k == '[ space ]':
			self.entryfield.insert(INSERT, ' ')
		elif k == 'submit':
			if self.validator:
				if not self.validator.validate(self.entryfield.get()):
					self.entryfield.configure(background = 'tomato2')
					return
			self.parent._destroy_popup()
		elif k == 'shift':
			for row in self.rows:
				for btn in row.winfo_children():
					if len(btn['text']) == 1:
						btn['text'] = self._changeCapital(btn['text'])
		else:
			self.entryfield.insert(INSERT, k)

	def _changeCapital(self, text):
		if text.isupper():
			return text.lower()
		return text.upper()
		

class KeyboardEntry(Frame):
	'''An extension/subclass of the Tkinter Entry widget, capable
	of accepting all existing args, plus args for each keyboard component (entry field and buttons) given as dictionaries
	Will pop up an instance of _PopupKeyboard when focus moves into
	the widget

	Usage:
	KeyboardEntry(parent, {"background":'white'},{}).pack()
	'''
	
	def __init__(self, parent, buttonsettings, entrysettings, validator=None, onSubmit=None, *args, **kwargs):
		Frame.__init__(self, parent)
		self.parent = parent
		self.entry = Entry(self, *args, **kwargs)
		self.entry.pack()
		#
		self.buttonsettings = buttonsettings
		self.entrysettings = entrysettings
		
		self.validator = validator
		self.onSubmit = onSubmit
		self.kbopen = False
		self.entry.bind('<ButtonRelease-1>', lambda e: self._check_entry_state('ButtonRelease-1'))

	def _check_entry_state(self, event):
		if not self.kbopen:
			self._call_popup()
		
	def _call_popup(self):
		print("Keyboard opened", flush=True)
		self.kb = _PopupKeyboard(attach=self.entry,
								 parent=self,
								 buttonsettings= self.buttonsettings,
								 entrysettings = self.buttonsettings,
								 validator=self.validator)
		self.kbopen = True

	def _destroy_popup(self):
		print("Keyboard destroyed", flush=True)
		self.entry.delete(0,END)
		self.entry.insert(0,self.kb.entryfield.get())
		self.kb._destroy_popup()
		self.kbopen = False
		if self.onSubmit and inspect.isfunction(self.onSubmit):
			self.onSubmit(self.text)
		
	@property
	def text(self):
		return self.entry.get()

class InputValidator(object, metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def validate(text):
		raise NotImplementedError('for usage please implement validate()')

import re
class RegexValidator(InputValidator):
	presets = {
	"ip": r"\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\b", #credits to: http://www.regular-expressions.info/ip.html
	"mail": r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", #credits to: http://emailregex.com/
	"url": r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+" #credits to: http://urlregex.com/
	}
	def __init__(self, regex):
		self.rege = re.compile(regex)
	def validate(self, text):
		return self.rege.match(text)
		
def test():  
	root = Tk()
	KeyboardEntry(root, {},{}).pack()
	KeyboardEntry(root, {'background':'gray'},{}, validator=RegexValidator(RegexValidator.presets["mail"])).pack()
	root.mainloop()
