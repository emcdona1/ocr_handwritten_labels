import tkinter.ttk as ttk
from tkinter import *

from ClassificationApp_GUI.OutputArea import UpdateOutput
from ClassificationApp_GUI.WordOutline import UpdateWordOutline
from DatabaseProcessing.DatabaseProcessing import UpdateTagInDatabase


class PopupWindow(object):
    def __init__(self, master, root, word, width, height):
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
        self.replacementEntry = ttk.Combobox(top, values=word['suggestedDescription'], width=100, font=("Courier", 16))
        self.replacementEntry.set(word['replacement'])
        self.replacementEntry.pack(expand=1)

        self.l2 = Label(top, text="Category:", justify="left", font=("Courier", 16))
        self.l2.pack(expand=0)
        self.categoryEntry = ttk.Combobox(top, values=root.WordCategories, width=100, font=("Courier", 16))
        self.categoryEntry.set(word['category'])
        self.categoryEntry.pack(expand=1)
        self.u = Button(self.top, text='Update', command=lambda: self.CommandUpdate(root, word),
                        activebackground='blue')
        self.c = Button(self.top, text='Cancel', command=self.CommandCancel, activebackground="blue")
        self.u.pack(side=RIGHT)
        self.c.pack(side=RIGHT)

    def CommandUpdate(self, root, word):
        self.ReplacementUpdate(word, self.replacementEntry.get(), root)
        self.CategoriesUpdate(root, word, self.categoryEntry.get())
        UpdateWordOutline(word)
        UpdateOutput(root)
        UpdateTagInDatabase(root.tagId, root.sdb)
        self.top.grab_release()
        self.top.destroy()

    def CategoriesUpdate(self, root, word, categoryValue):
        oldValue = word['category']
        if oldValue != categoryValue:
            word['category'] = categoryValue
            UpdateTagInDatabase(root.tagId, root.sdb)
            if categoryValue not in root.WordCategories:
                root.WordCategories.append(categoryValue)

    def ReplacementUpdate(self, word, replacementValue, root):
        oldValue = word['replacement']
        if oldValue != replacementValue:
            word['replacement'] = replacementValue
            if word['description'] == replacementValue:
                word['color'] = 'green'
                word['isIncorrectWord'] = False
            else:
                word['color'] = '#F4A460'  # user updated values
                word['isIncorrectWord'] = True
            if oldValue not in word['suggestedDescription']:
                word['suggestedDescription'].append(oldValue)

    def CommandCancel(self):
        self.top.grab_release()
        self.top.destroy()
