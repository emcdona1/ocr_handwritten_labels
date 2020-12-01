import tkinter.ttk as ttk
from tkinter import *
from tkinter.scrolledtext import ScrolledText

from ClassificationApp_GUI.OutputArea import UpdateOutput
from ClassificationApp_GUI.WordOutline import UpdateWordOutline
from DatabaseProcessing.DatabaseProcessing import UpdateWordInDatabase


class PopupWindowEditConfig(object):
    def __init__(self, master, root, configFilePath):
        width = 1000
        height = 600
        top = self.top = Toplevel(master)
        self.configFilePath=configFilePath
        self.top.grab_set()
        self.root=root
        self.top.geometry(str(width) + "x" + str(height))
        self.top.resizable(1, 1)
        self.top.wm_title("Update configurations" )
        self.top.configure(padx=2, pady=2)

        #pop up box layout
        buttonFrame = Frame(top, height=0, width=0)
        buttonFrame.pack(anchor=SE, expand=True, side=BOTTOM)

        textAreaFrame=Frame(top, height=0,width=0)
        textAreaFrame.pack(anchor=NW, expand=True,fill=BOTH, side=TOP)

        self.outputField = ScrolledText(textAreaFrame, height=100,font=("Courier", 16), bd=0, highlightthickness=0)
        self.outputField.pack(padx=0, pady=2, fill=BOTH, expand=True)
        ConfigureFieldStyle(self)

        DisplayConfigurations(self,self.configFilePath)


        u = Button(buttonFrame, text='Update', command=self.CommandUpdate,
                        activebackground='blue')
        u.grid(row=0, column=0, sticky='se')
        c = Button(buttonFrame, text='Cancel', command=self.CommandCancel, activebackground="blue")
        c.grid(row=0, column=1, sticky='se')

    def CommandUpdate(self):
        configFile=open(self.configFilePath,"w")
        configurations=self.outputField.get('1.0',END)
        configFile.write(configurations)
        configFile.close()
        try:
            self.root.destroy()
        except Exception as e:
            raise Exception('Restart', 'Restart application due to configuration update!')

    def CommandCancel(self):
        self.top.grab_release()
        self.top.destroy()


def ConfigureFieldStyle(root):
    root.outputField.tag_config('section', foreground="blue",font=("Courier", 14))
    root.outputField.tag_config('key', foreground="orange",font=("Courier", 14))
    root.outputField.tag_config('value', foreground="green",font=("Courier", 14))
    root.outputField.tag_config('sign', foreground="red",font=("Courier", 14))

def DisplayConfigurations(self,configFilePath):
    configFile=open(configFilePath,"r")
    configurations=configFile.readlines()
    configFile.close()
    for line in configurations:
        if(len(line))>0:
            if(line[0]=='['):
                self.outputField.insert(END,line,'section')
            else:
                if('=' in line):
                    key,val= line.split('=',1)
                    self.outputField.insert(END,key,'key')
                    self.outputField.insert(END,'=','sign')
                    self.outputField.insert(END,val,'value')
                else:
                    self.outputField.insert(END,line)
        else:
            self.outputField.insert(END,line)
