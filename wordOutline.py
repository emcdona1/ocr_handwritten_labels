def updateWordOutline(word):
    if word['index']>0:
       if(word['color']=='green'):
            word['canvas'].itemconfigure(word['polygon'], outline='', width=1,
                                           fill='',    activeoutline=word['color'],activewidth=2)
       else:
           word['canvas'].itemconfigure(word['polygon'], outline=word['color'], width=1,
                                          fill='',    activeoutline=word['color'], activewidth=2)