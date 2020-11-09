import tkinter.ttk as ttk
from tkinter import *

from ClassificationApp_GUI.OutputArea import UpdateOutput
from ClassificationApp_GUI.WordOutline import UpdateWordOutline
from DatabaseProcessing.DatabaseProcessing import UpdateWordInDatabase


class PopupWindow(object):
    def __init__(self, master, root, word):
        rowHeight=35
        padding=2
        width = 365
        height=rowHeight*4-padding*8
        top = self.top = Toplevel(master)
        self.top.grab_set()
        self.tagId=root.tagId
        self.root=root
        self.word=word
        self.top.geometry(str(width) + "x" + str(height))
        self.top.resizable(0, 0)
        self.top.wm_title("Manual update: " + word['description'])
        self.top.configure(padx=padding, pady=padding)

        #pop up box layout
        wordDiscriptionFrame=Frame(top, height=rowHeight, pady=padding)
        wordDiscriptionFrame.grid(row=0, column=0, sticky='nsew')

        replacementFrame = Frame(top, height=rowHeight,  pady=padding)
        replacementFrame.grid(row=1, column=0, sticky='nsew')

        categoryFrame = Frame(top, height=rowHeight,  pady=padding)
        categoryFrame.grid(row=2, column=0, sticky='nsew')

        buttonFrame = Frame(top, height=rowHeight, width=width, pady=padding)
        buttonFrame.grid(row=3, column=0, sticky='se')

        l1 = Label(wordDiscriptionFrame, text="Word       : " + word['description'], justify="left", font=("Courier", 16))
        l1.grid(row=0,column=0,sticky='nw')

        l2 = Label(replacementFrame, text="Replacement:", justify="left", font=("Courier", 16))
        l2.grid(row=0, column=0, sticky='nw')

        self.replacementEntry = ttk.Combobox(replacementFrame, values=word['suggestedDescription'], width=20, font=("Courier", 16))
        self.replacementEntry.set(word['replacement'])
        self.replacementEntry.grid(row=0, column=1, sticky='ne')


        l3 = Label(categoryFrame, text="Category   :", justify="left", font=("Courier", 16))
        l3.grid(row=0, column=0, sticky='nw')

        self.categoryEntry = ttk.Combobox(categoryFrame, values=root.WordCategories, width=20, font=("Courier", 16))
        self.categoryEntry.set(word['category'])
        self.categoryEntry.grid(row=0, column=1, sticky='ne')

        u = Button(buttonFrame, text='Update', command=self.CommandUpdate,
                        activebackground='blue')
        u.grid(row=0, column=0, sticky='se')
        c = Button(buttonFrame, text='Cancel', command=self.CommandCancel, activebackground="blue")
        c.grid(row=0, column=1, sticky='se')

    def CommandUpdate(self):
        self.ReplacementUpdate(self.replacementEntry.get())
        self.CategoriesUpdate(self.categoryEntry.get())
        self.root.tagId=self.tagId
        UpdateWordInDatabase(self.root,self.word)
        UpdateWordOutline(self.word)
        UpdateOutput(self.root)
        self.top.grab_release()
        self.top.destroy()

    def CategoriesUpdate(self,categoryValue):
        oldValue = self.word['category']
        if oldValue != categoryValue:
            self.word['category'] = categoryValue
            if categoryValue not in self.root.WordCategories:
                self.root.WordCategories.append(categoryValue)

    def ReplacementUpdate(self, replacementValue):
        oldValue = self.word['replacement']
        if oldValue != replacementValue:
            self.word['replacement'] = replacementValue
            if self.word['description'] == replacementValue:
                self.word['color'] = 'green'
                self.word['isIncorrectWord'] = False
            else:
                self.word['color'] = '#F4A460'  # user updated values
                self.word['isIncorrectWord'] = True
            if oldValue not in self.word['suggestedDescription']:
                self.word['suggestedDescription'].append(oldValue)

    def CommandCancel(self):
        self.top.grab_release()
        self.top.destroy()
