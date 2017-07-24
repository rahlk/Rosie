#-------------------------------------------------------------------------------
# Name:        Application
# Purpose:
#
# Author:      Daniel Beall
#
# Created:     30/08/2013
# Copyright:   None! :)
# Licence:     MIT
#-------------------------------------------------------------------------------

from Tkinter import *
from tkFileDialog import askopenfilename
import tkMessageBox
class Application(Frame):



    def __init__(self, master):
        Frame.__init__(self,master)
        self.grid()
        self.create_widgets()
        self.topbar()

#open a txt file
    def filesystem_access(self):
        filename = open(askopenfilename(filetypes=[("allfiles","*"),("textfiles","*.txt")]))
        fetchedstring = filename.read()
        self.outputfromfile(fetchedstring)
#save to a text file
    def savetofilesystem(self):
          filename = open(askopenfilename(filetypes=[("textfiles - will overwrite","*.txt")]),"w")
          filename.write(self.text.get(0.0,END))

    def create_widgets(self):
        self.instruction = Label(self, text = "Insert Text in Box")
        self.instruction.grid(row = 0,  column =0, columnspan = 2, sticky = W)

        self.phonenumberletters = Entry(self)
        self.phonenumberletters.grid(row = 1, column = 1, sticky = W)

        self.submit_button = Button(self, text = "Submit", command = self.reveal)
        self.submit_button.grid(row =2, column = 0, sticky =W)

        self.delete_button = Button(self, text = "Clear", command = self.delete)
        self.delete_button.grid(row =2, column = 1, sticky =W)

        self.text = Text(self, width = 35, height = 15, wrap = WORD)
        self.text.grid(row = 3, column = 0, columnspan =2, sticky = W)



# makes Menu Bars
    def topbar(self):
        menubar = Menu(root)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.filesystem_access)
        filemenu.add_command(label="Save", command=self.savetofilesystem)

        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.hello)
        menubar.add_cascade(label="Help", menu=helpmenu)


        root.config(menu=menubar)

# displays About my app
    def hello(self):
        tkMessageBox.showinfo("Help - Phone Verter <2013>", "Version 1.5 \n Licensed Under the MIT license \n Built and maintained by Daniel Beall \n Contact: thedan16@users.sourceforge.net  ")

#output when button is pressed
    def reveal(self):
        #take input from text box
        phonestring = self.phonenumberletters.get().lower()
        phone = {"a": "2", "b": "2", "c": "2", "d": "3", "e": "3", "f" : "3", "g": "4", "h": "4", "i": "4",
        "j": "5", "k": "5", "l": "5", "m": "6", "n": "6", "o": "6", "p": "7", "q": "7","r": "7", "s": "7", "t": "8", "u": "8", "v": "8", "w": "9", "x": "9", "y": "9", "z": "9"}
        finalstring = ""
        for z in range(0, len(phonestring)):
            if phone.has_key(phonestring[z])  == True:
                finalstring = finalstring + phone[phonestring[z]]
            else:
                finalstring = finalstring + phonestring[z]

        self.text.insert(0.0, finalstring)

    #output from a text file
    def outputfromfile(self, fileinput):
        phonestring = fileinput.lower()
        phone = {"a": "2", "b": "2", "c": "2", "d": "3", "e": "3", "f" : "3", "g": "4", "h": "4", "i": "4",
        "j": "5", "k": "5", "l": "5", "m": "6", "n": "6", "o": "6", "p": "7", "q": "7","r": "7", "s": "7", "t": "8", "u": "8", "v": "8", "w": "9", "x": "9", "y": "9", "z": "9"}
        finalstring = ""
        for z in range(0, len(phonestring)):
            if phone.has_key(phonestring[z])  == True:
                finalstring = finalstring + phone[phonestring[z]]
            else:
                finalstring = finalstring + phonestring[z]

        self.text.insert(0.0, finalstring)


    #clear Text Area
    def delete(self):
        self.text.delete(0.0, END)



root = Tk()
root.title("PhoneVerter")
root.geometry("350x400")
app = Application(root)

root.mainloop()
