from tkinter import *
import tkinter.ttk as ttk

from globalCalls import setToDefaultWord, updateOutput


class popupWindow(object):
    def __init__(self, master, root,word, width, height):
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
        self.replacementEntry = ttk.Combobox(top, values=word['suggestedDescription'],width=100,font=("Courier", 16) )
        self.replacementEntry.set(word['replacement'])
        self.replacementEntry.pack(expand=1)

        self.l2 = Label(top,text="Category:", justify="left", font=("Courier", 16) )
        self.l2.pack(expand=0)
        self.categoryEntry = ttk.Combobox(top, values=root.categories, width=100, font=("Courier", 16))
        self.categoryEntry.set(word['category'])
        self.categoryEntry.pack(expand=1)




        self.u = Button(self.top, text='Update', command=lambda: self.commandUpdte(root,word), activebackground='blue')
        self.c = Button(self.top, text='Cancel', command=self.commandCancel, activebackground="blue")
        self.u.pack(side=RIGHT)
        self.c.pack(side=RIGHT)

    def commandUpdte(self,root, word):
        self.replacementUpdate(word, self.replacementEntry.get())
        self.categoriesUpdate(root,word,self.categoryEntry.get() )

        setToDefaultWord(word)
        updateOutput(root)
        self.top.grab_release()
        self.top.destroy()

    def categoriesUpdate(self,root, word, categoryValue):
        oldValue = word['category']
        if oldValue != categoryValue:
            word['category'] = categoryValue
            if categoryValue not in root.categories:
                root.categories.append(categoryValue)


    def replacementUpdate(self,word, replacementValue):
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

    def commandCancel(self):
        self.top.grab_release()
        self.top.destroy()
