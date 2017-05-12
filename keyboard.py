﻿'''Popup Keyboard is a module to be used with Python's Tkinter library
It subclasses the Entry widget as KeyboardEntry to make a fullscreen pop-up
keyboard appear as the widget gains focus. Development in progress and focused to use with small touchscreens.
'''

from tkinter import *
import math

class _PopupKeyboard(Toplevel):
    '''A Toplevel instance that displays a keyboard that is attached to
    another widget. Only the Entry widget has a subclass in this version.
    '''
    
    def __init__(self, parent, attach, keycolor, keysize=0):
        Toplevel.__init__(self, takefocus=0)
        
        self.overrideredirect(True)
        self.attributes('-alpha',0.95)
        self.parent = parent
        self.attach = attach
        self.keysize = keysize
        self.keycolor = keycolor
        self.keyframe = Frame(self)
        self.toprow = Frame(self.keyframe)

        self.delete = '←'
        self.keys = [
            ([i for i in range(0,10)]),
            ['q', 'w', 'e', 'r', 't', 'z', 'u', 'i', 'o', 'p', '/', self.delete],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l',','],
            ['shift','y', 'x', 'c', 'v', 'b', 'n', 'm','.','?'],
            ['@','#','%','*','[ space ]','+','-','=', 'submit']
            ]
        self.keyframe.pack()
        self.keyframe.place(x=0,y=0)
        self.toprow.grid(row=1)
        self.rows = {}
        for	i in range(len(self.keys)):
            self.rows[i] = Frame(self.keyframe)
            self.rows[i].grid(row=i+2)
		
        self.keycount = max([len(n) for n in self.keys])
        if self.keysize == 0:
            self.keysize = math.floor(self.winfo_width() / self.keycount)
        spw = self.parent.winfo_screenwidth() - self.winfo_reqwidth() #calulate space to the sides
        if spw > 0:
            self.x = math.floor(spw/2) #center keyboard
        sph = self.parent.winfo_screenheight() - self.winfo_reqheight()
        if sph > 0:
            self.y = math.floor(sph/2)
		
        
        self._init_keys()

        self.update_idletasks()
        self.geometry('{}x{}+{}+{}'.format(self.parent.winfo_screenwidth(),
                                           self.parent.winfo_screenheight(),
                                           0,0))
        #self.mainframe.geometry('{}x{}+{}+{}'.format(self.winfo_width(),self.winfo_height(),self.x,self.y))
        self.bind('<FocusOut>', lambda e: self._check_kb_state('focusout'))
        self.bind('<Return>', lambda e: self._check_kb_state('return'))

    def _check_kb_state(self, event):
        if (event == 'focusout' and not (self.focus_get() == self or self.parent.focus_get() == self.parent)) or event == 'return':
            self.parent._destroy_popup()

    def _init_keys(self):
        self.entryfield = Entry(self.toprow)
        self.entryfield.pack(anchor=CENTER)
        self.entryfield.insert(END,self.attach.get())
        i = 0
        for row in self.keys:
            for key in row:
                multiplier = 1
                b = Button(self.rows[i], text=key, width = self.keysize, bg=self.keycolor)
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
            self.attach.delete(0,END)
            self.attach.insert(END, self.entryfield.get())
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
    of accepting all existing args, plus a keysize and keycolor option.
    Will pop up an instance of _PopupKeyboard when focus moves into
    the widget

    Usage:
    KeyboardEntry(parent, keysize=6, keycolor='white').pack()
    '''
    
    def __init__(self, parent, keysize=0, keycolor='gray', *args, **kwargs):
        Frame.__init__(self, parent)
        self.parent = parent
        
        self.entry = Entry(self, *args, **kwargs)
        self.entry.pack()

        self.keysize = keysize
        self.keycolor = keycolor
        
        self.kbopen = False
        self.entry.bind('<ButtonRelease-1>', lambda e: self._check_entry_state('ButtonRelease-1'))

    def _check_entry_state(self, event):
        if not self.kbopen:
            self._call_popup()
        
    def _call_popup(self):
        self.kb = _PopupKeyboard(attach=self.entry,
                                 parent=self,
                                 keysize=self.keysize,
                                 keycolor=self.keycolor)
        self.kbopen = True

    def _destroy_popup(self):
        self.entry.delete(0,END)
        self.entry.insert(0,self.kb.entryfield.get())
        self.kb._destroy_popup()
        self.kbopen = False

def test():  
    root = Tk()
    KeyboardEntry(root, keycolor='white').pack()
    KeyboardEntry(root).pack()
    root.mainloop()
