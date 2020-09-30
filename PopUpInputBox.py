from tkinter import *
import tkinter.ttk as ttk

from globalCalls import setToDefaultWord, updateOutput


class popupWindow(object):
    def __init__(self, master, word, width, height):
        top = self.top = Toplevel(master)
        self.top.grab_set()

        self.top.geometry(str(width) + "x" + str(height))
        self.top.resizable(0, 0)
        self.top.wm_title("Manual update: " + word['description'])
        self.top.configure(padx=10, pady=10)
        self.l1 = Label(top, text="Word      :" + word['description']
                                  + "\nConfidence:" + '{: <18}'.format(str(word['confidence']))
                                  + "\n\nReplacement:", justify="left", font=("Courier", 16))
        self.l1.pack(expand=1)
        self.e = ttk.Combobox(top, values=word['suggestedDescription'],width=100,font=("Courier", 16) )
        self.e.set(word['replacement'])
        self.e.pack(expand=1)

        self.u = Button(self.top, text='Update', command=lambda: self.commandUpdte(word), activebackground='blue')
        self.c = Button(self.top, text='Cancel', command=self.commandCancel, activebackground="blue")
        self.u.pack(side=RIGHT)
        self.c.pack(side=RIGHT)

    def commandUpdte(self, word):
        oldValue = word['replacement']
        newValue = self.e.get()
        if oldValue != newValue:
            word['replacement'] = newValue
            if word['description'] == newValue:
                word['color'] = 'green'
                word['isIncorrectWord'] = False
            else:
                word['color'] = '#F4A460'  # user updated values
                word['isIncorrectWord'] = True
            if oldValue not in word['suggestedDescription']:
                word['suggestedDescription'].append(oldValue)
            setToDefaultWord(word)
            updateOutput()

        self.top.grab_release()
        self.top.destroy()

    def commandCancel(self):
        self.top.grab_release()
        self.top.destroy()
