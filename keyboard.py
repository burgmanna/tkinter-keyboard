'''Popup Keyboard is a module to be used with Python's Tkinter library
It subclasses the Entry widget as KeyboardEntry to make a pop-up
keyboard appear when the widget gains focus. Still early in development.
'''

from tkinter import *
import math

class _PopupKeyboard(Toplevel):
    '''A Toplevel instance that displays a keyboard that is attached to
    another widget. Only the Entry widget has a subclass in this version.
    '''
    
    def __init__(self, parent, attach, keycolor, keysize=5):
        Toplevel.__init__(self, takefocus=0)
        
        self.overrideredirect(True)
        self.attributes('-alpha',0.95)
        self.parent = parent
        self.attach = attach
        self.keysize = keysize
        self.keycolor = keycolor
        self.mainframe = Frame(self)
        self.toprow = Frame(self.mainframe)

        self.delete = '←'
        self.alpha = {
            '1' : ['q', 'w', 'e', 'r', 't', 'z', 'u', 'i', 'o', 'p', '/', self.delete],
            '2' : ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l',','],
            '3' : ['shift','y', 'x', 'c', 'v', 'b', 'n', 'm','.','?','[1,2,3]'],
            '4' : ['@','#','%','*','space','+','-','=', 'submit']
            } #somewhat of a workaround, maybe re-write this?
        self.mainframe.pack()
        self.mainframe.place(x=0,y=0)
        self.toprow.grid(row=1)
        self.rows = {}
        for	i in range(len(self.alpha.keys())):
            self.rows[str(i+1)] = Frame(self.mainframe)
            self.rows[str(i+1)].grid(row=i+2)
		
        self.keycount = max([len(n) for n in self.alpha.values()])
        self.keysize = math.floor(self.winfo_width() / self.keycount)
        spw = self.parent.winfo_screenwidth() - self.winfo_reqwidth() #calulate space to the sides
        self.x = math.floor(spw/2) #center keyboard
        sph = self.parent.winfo_screenheight() - self.winfo_reqheight()
        self.y = math.floor(sph/2)
		
        
        self._init_keys()

        self.update_idletasks()
        self.geometry('{}x{}+{}+{}'.format(self.parent.winfo_screenwidth(),
                                           self.parent.winfo_screenheight(),
                                           0,0))
        #self.mainframe.geometry('{}x{}+{}+{}'.format(self.winfo_width(),self.winfo_height(),self.x,self.y))
        self.bind('<FocusOut>', lambda e: self._check_state('focusout'))
        self.bind('<Return>', lambda e: self._check_state('return'))

    def _check_state(self, event):
        if (event == 'focusout' and not (self.focus_get() == self or self.parent.focus_get() == self.parent)) or event == 'return':
            self.parent._destroy_popup()

    def _init_keys(self):
        self.entryfield = Entry(self.toprow)
        self.entryfield.pack(anchor=CENTER)
        self.entryfield.insert(END,self.attach.get())
        for i in self.alpha.keys():
            for k in self.alpha[i]:
                multiplier = 1
                b = Button(self.rows[i], text=k, width = self.keysize, bg=self.keycolor)
                b.bind("<ButtonRelease-1>", self._attach_key_press)
                b.grid(row=0, column=self.alpha[i].index(k))

    def _destroy_popup(self):
        self.destroy()

    def _attach_key_press(self, btn):
        k = btn.widget['text']
        if k == self.delete:
            self.entryfield.delete(len(self.entryfield.get())-1, END)
        elif k == '[1,2,3]':
            pass
        elif k == '[ space ]':
            self.entryfield.insert(END, ' ')
        elif k == 'submit':
            self.attach.delete(0,END)
            self.attach.insert(END, self.entryfield.get())
            self.parent._destroy_popup()
        elif k == 'shift':
            for r in self.rows.keys():
                for btn in self.rows[r].winfo_children():
                    if len(btn['text']) == 1:
                        btn['text'] = self._changeCapital(btn['text'])
        else:
            self.entryfield.insert(END, k)

    def _changeCapital(self, text):
        if text.isupper():
            return text.lower()
        return text.upper()
'''
TO-DO: Implement Number Pad
class _PopupNumpad(Toplevel):
    def __init__(self, x, y, keycolor='gray', keysize=5):
        Toplevel.__init__(self, takefocus=0)
        
        self.overrideredirect(True)
        self.attributes('-alpha',0.85)

        self.numframe = Frame(self)
        self.numframe.grid(row=1, column=1)

        self.__init_nums()

        self.update_idletasks()
        self.geometry('{}x{}+{}+{}'.format(self.winfo_width(),
                                           self.winfo_height(),
                                           self.x,self.y))

    def __init_nums(self):
        i=0
        for num in ['7','4','1','8','5','2','9','6','3']:
            print num
            Button(self.numframe,
                   text=num,
                   width=int(self.keysize/2),
                   bg=self.keycolor,
                   command=lambda num=num: self.__attach_key_press(num)).grid(row=i%3, column=i/3)
            i+=1
'''

class KeyboardEntry(Frame):
    '''An extension/subclass of the Tkinter Entry widget, capable
    of accepting all existing args, plus a keysize and keycolor option.
    Will pop up an instance of _PopupKeyboard when focus moves into
    the widget

    Usage:
    KeyboardEntry(parent, keysize=6, keycolor='white').pack()
    '''
    
    def __init__(self, parent, keysize=5, keycolor='gray', *args, **kwargs):
        Frame.__init__(self, parent)
        self.parent = parent
        
        self.entry = Entry(self, *args, **kwargs)
        self.entry.pack()

        self.keysize = keysize
        self.keycolor = keycolor
        
        self.kbopen = False
        self.entry.bind('<ButtonRelease-1>', self._check_state)

    def _check_state(self):
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
    KeyboardEntry(root, keysize=6, keycolor='white').pack()
    KeyboardEntry(root).pack()
    root.mainloop()
