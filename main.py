from classificationGUI import ClassificationApp, processTagImage
def printSdb(sdb):
    text = ""
    for b in sdb:
        for w in b:
            text += w['description'] + " "
        text += "\n"
    print(text)
if __name__ == '__main__':
    '''
    imagePath="/Users/Keshab/Desktop/Tags/1.jpg"
    sdb = processTagImage(imagePath, .99)
    printSdb(sdb)

    imagePath = "/Users/Keshab/Desktop/Tags/3.jpg"
    sdb=processTagImage(imagePath, .99)
    printSdb(sdb)
    '''
    classificationApp = ClassificationApp()



