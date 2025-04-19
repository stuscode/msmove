#!/usr/bin/env python3

import argparse
from calendar import month_name
import datetime
import copy
import os
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import *
import threading
import time
import queue
import signal
import watchdog.events
import watchdog.observers
import yaml

INFOFILE='.msmoveproto'
DEFAULTRENAME='statement_%Y%m'
INTERESTINGEXTENSIONS=('pdf','ps')
 
class window(tk.Tk):
   def __init__(self, workqueue, srcdir, destdirtree):
      super().__init__()
      self.work = workqueue
      self.observer = None
      self.srcdir = srcdir
      self.destdirtree = destdirtree
      self.endqueue = False
      self.name = ''

   def wincreate(self):
      row = 0
      self.wm_title("msmove")
      self.grid_columnconfigure(2, weight=1)

      self.srclabel = Label(self, text="source:")
      self.srclabel.grid(row=row, column= 0)
      self.srcname = Label(self, width=40)
      self.srcname.grid(row=row, column=1, columnspan=3)
      self.cancelbutton = Button(self, text="Exit",command=self.destroywin)
      self.cancelbutton.grid(row=row,column=4)
      row = row + 1
      self.destlabel = Label(self, text="dest:")
      self.destlabel.grid(row=row, column= 0)
      self.destnamevar = tk.StringVar()
      self.destname = Entry(self, width=40, textvar=self.destnamevar)
      self.destname.grid(row=row, column=1, columnspan=2)
      self.dobutton = Button(self, text="Move",command=self.doit)
      self.dobutton.grid(row=row,column=3)
      self.skipbutton = Button(self, text="Skip",command=self.doit)
      self.skipbutton.grid(row=row,column=4)
      row = row + 1
      self.sep1 = ttk.Separator(self,orient=tk.HORIZONTAL)
      self.sep1.grid(row=row, column=0, columnspan=5, sticky='ew')
      row = row + 1
      self.forcelabel = Label(self, text="force date:")
      self.forcelabel.grid(row=row, column= 0)
      self.forcemonth = monthsel(self)
      self.forcemonth.grid(row=row, column = 1)
      self.forceyear = yearsel(self)
      self.forceyear.grid(row=row, column = 2)
      self.forceckboxvar = IntVar()
      self.forceckbox = ttk.Checkbutton(self, text='Use this as date', variable=self.forceckboxvar)
      self.forceckbox.state(['!selected'])
      self.forceckbox.grid(row=row, column=3, columnspan=2)
      row = row + 1
      self.sep1 = ttk.Separator(self,orient=tk.HORIZONTAL)
      self.sep1.grid(row=row, column=0, columnspan=5, sticky='ew')
      row = row + 1
      self.srcdirlab = Label(self, text="source dir:")
      self.srcdirlab.grid(row=row, column=0)
      self.srcdirdis = Label(self, text=srcdir)
      self.srcdirdis.grid(row=row, column=1, columnspan=3)
      self.srcdirsel = Button(self, text="Sel",command=self.picsrcdir)
      self.srcdirsel.grid(row=row, column=4)
      row = row + 1
      self.sep1 = ttk.Separator(self,orient=tk.HORIZONTAL)
      self.sep1.grid(row=row, column=0, columnspan=5, sticky='ew')
      row = row + 1
      self.dstdirlab = Label(self, text="dest dirs:")
      self.dstdirlab.grid(row=row, column=0)
      self.dstdirdis = Label(self,width=40, text=self.destdirtree)
      self.dstdirdis.grid(row=row, column=1, columnspan=3)
      self.dstdirsel = Button(self, text="Sel",command=self.picdstdir)
      self.dstdirsel.grid(row=row, column=4)
      row = row + 1
      self.sep1 = ttk.Separator(self,orient=tk.HORIZONTAL)
      self.sep1.grid(row=row, column=0, columnspan=5, sticky='ew')
      row = row + 1
      self.showlessvar = IntVar()
      self.showless = ttk.Checkbutton(self,text='Show less used', variable = self.showlessvar)
      self.showless.state(['!selected'])
      self.showless.grid(row=row, column=0,columnspan=2, sticky='e')
      self.islessvar = IntVar()
      self.isless = ttk.Checkbutton(self,text='Entry is less used', variable= self.islessvar)
      self.isless.state(['!selected'])
      self.isless.grid(row=row, column=3,columnspan=2, sticky='w')
      row = row + 1
      self.sep1 = ttk.Separator(self,orient=tk.HORIZONTAL)
      self.sep1.grid(row=row, column=0, columnspan=5, sticky='ew')
      row = row + 1
      self.pattlabel = Label(self, text="pattern:")
      self.pattlabel.grid(row=row, column= 0)
      self.pattnamevar = tk.StringVar()
      self.pattname = Entry(self, width=40, textvar=self.pattnamevar)
      self.pattname.grid(row=row, column=1, columnspan=3)
      self.pattbutton = Button(self, text="Save",command=self.usermodidpat)
      self.pattbutton.grid(row=row,column=4)
      row = row + 1
      self.grid_rowconfigure(row,weight=1)
      self.dirlist=dirlistpanel(self)
      self.dirlist.grid(row=row,column=0,columnspan=5,sticky='nsew')

      #This makes tk responsive to control-C from launching terminal
   def check(self):
      self.after(500,self.check)

   def run(self):
      self.observer_restart()
      self.wincreate()
      self.setdirlist()
      self.workget = threading.Thread(target=self.getworkthread)
      self.workget.start()
      self.lift() #maybe
      self.attributes('-topmost', True) #maybe
      self.check()
      self.mainloop()

   def usermodidpat(self):
      print("save id pattern back to file and update scores")

   def setdirlist(self):
      self.dirlist.settopdir(self.destdirtree)

   def userdirselection(self, idpattern,renamepattern):
      print(idpattern, renamepattern)
      if len(renamepattern) == 0:
         self.renamepattern = DEFAULTRENAME
      else:
         self.renamepattern = renamepattern
#TODO set pattern field from idpattern

   def observer_restart(self):
      if self.observer != None:
         self.observer_end()
      self.observer = watchdog.observers.Observer()
      event_handler = eventhandle()
      event_handler.setqueue(self.work)
      self.observer.schedule(event_handler, self.srcdir, recursive = False)
      self.observer.start()

   def observer_end(self):
      self.observer.stop()
      self.observer.join()

   def picsrcdir(self):
      newdir = filedialog.askdirectory()
      if len(newdir) > 0:
         self.srcdirdis.config(text=newdir)

   def picdstdir(self):
      newdir = filedialog.askdirectory()
      if len(newdir) > 0:
         self.dstdirdis.config(text=newdir)
         self.dirlist.settopdir(newdir)

   def doit(self):
         #get dest dir
      dest = self.dirlist.getselecteddir()
         #set dest name
         #execute copy from self.name to destdir/destname
      print("process ",self.name)

   def setdestfilename(self):
      destpat = self.dirlist.getselectedrenamepat()
      if self.forceckboxvar.get() == 1:
         years = self.forceyear.cget("text")
         year = int(years)
         month = self.forcemonth.get() + 1  #zero based
         ymd = "%4d%2d01" % (year, month)
         time = datetime.datetime.fromisoformat('yyyymmdd')
      else:
         time = datetime.datetime.now()
      self.destfilename = time.strftime(destpat)
      self.destname.delete(0, END)
      self.destname.insert(0, self.destfilename)

   def getworkthread(self):
      while True:
         self.name = self.work.get()
         if self.endqueue:
            break
         self.srcname.config(text=os.path.basename(self.name))
         self.setdestfilename()

#TODO use self.renamepattern to set destination name
         self.lift() #maybe
         self.attributes('-topmost', True) #maybe

   def finishwin(self):
      self.destroy()

   def finishup(self):
      self.endqueue = True
      self.observer_end()
      work.put("")  #wake up the get so thread can exit

   def destroywin(self):
      self.destroy()


class monthsel(ttk.Combobox):
   def __init__(self, s):
      super().__init__(s,width=8)
      self['values'] = [month_name[m][0:3]+' ('+str(m)+')' for m in range(1, 13)]
      self.current(newindex=datetime.datetime.now().month-1)

class yearsel(Entry):
   def __init__(self, s):
      self.yearvar = tk.StringVar()
      super().__init__(s,textvar = self.yearvar, width=6)
      self.yearvar.set(str(datetime.datetime.now().year))

class dirlistpanel(Frame):
   def __init__(self, c):
      super().__init__(c)
      self.select_cb = c  
      self.listvar = Variable()
      self.grid_rowconfigure(0,weight=1)
      self.grid_columnconfigure(0,weight=1)
      self.list = Listbox(self, height=20, listvariable=self.listvar, exportselection=False)
      self.list.grid(row=0,column=0,sticky='nsew')
      self.vscroll = ttk.Scrollbar(self,orient=tk.VERTICAL,command=self.list.yview)
      self.list['yscrollcommand'] = self.vscroll.set
      self.vscroll.grid(row=0,column=1,sticky='ns')
      self.list.bind('<<ListboxSelect>>', self.userselect)

   def settopdir(self, topdir):
      self.dirlist=[]
      self.displaylist = []
      self.topdir = topdir
      subfolders = [ f for f in os.scandir(topdir) if f.is_dir() and not f.name.startswith('.') ]
      sortedsubf = sorted(subfolders, key=lambda s: s.name.lower())
#      subfolders.sort()
      for d in sortedsubf:
         self.displaylist.append(d.name)
         (newname, pattern) = self.getinfo(d)
         self.dirlist.append(destdir(d, newname, pattern))
      self.listvar.set(self.displaylist)
      self.list.select_set(0)  #as if first row selected
      self.selectrow(0) #set up variables
#get info for directories

         #we are setting a row programmatically
   def selectrow(self, row):  #row 0 based
      self.select_cb.userdirselection(self.dirlist[row].idpattern,self.dirlist[row].renamepattern)

   def getinfo(self,d):
      protopath = os.path.join(d.path, INFOFILE)
      if os.path.isfile(protopath):
         with open(protopath, 'r') as stream:
            protodata = yaml.safe_load(stream)
            return (protodata['newname'], protodata['pattern'])
      return ('','')

             #user clicked on a row
   def userselect(self, event):
      s = self.list.curselection()
      if len(s) == 1:
         self.selectrow(s[0])

   def getselecteddir(self):
      row = self.list.curselection()[0] #single select mode, and we always have something selected.
      full = os.path.join(self.topdir, self.dirlist[row].path)
      return full

   def getselectedidpat(self):
      row = self.list.curselection()[0] #single select mode, and we always have something selected.
      full = os.path.join(self.topdir, self.dirlist[row].idpattern)
      return full

   def getselectedrenamepat(self):
      row = self.list.curselection()[0] #single select mode, and we always have something selected.
      pat = self.dirlist[row].renamepattern
      if len(pat) == 0:
         pat = DEFAULTRENAME
      full = os.path.join(self.dirlist[row].path, pat)
      return full

class destdirlist():
   def setdirs(self, dirlist):
      self.dirs = dirlist
   def getdirs(self):
      return self.dirs

class destdir():
   def __init__(self, path, idpattern, newname):
      self.path = path
      self.idpattern = idpattern
      self.renamepattern = newname

class eventhandle(watchdog.events.FileSystemEventHandler):
   work = None
   def setqueue(self, queue):
      self.work = queue

#@staticmethod
   def on_moved(self, event):
          #this is the move after the browser finishes download
      dest = event.dest_path
      lowerdest = dest.lower()
      for ext in INTERESTINGEXTENSIONS:
         if lowerdest.endswith(ext):
            self.work.put(dest)
            break

class sighandle():
   win = None

   def setwin(self,window):
      self.win = window

   def sigint_handler(self, sig, frame):
      print("signal")
      self.win.finishwin()
      self.win.finishup()

#program
#  hide dirs
#directories
# name a
#  lessused: false
#  newname: prototype
#  pattern: match pattern
# name b
#  lessused: false
#  newname: prototype
#  pattern: match pattern
class configfile():
   def __init__(self):
      self.loadconfig()
   def loadconfig(self):
      print('a')
   def writeconfig(self):
      print('b')
      

def arguments():
   p = argparse.ArgumentParser(description="move monthly statements")
   p.add_argument('srcdir')
   p.add_argument('destdirtree')
   args = p.parse_args();
   return(args.srcdir, args.destdirtree)
 
if __name__ == '__main__':
   global win
        #process command line arguments
   (srcdir, destdirtree) = arguments()
   config = configfile()
   work = queue.Queue()
   sig = sighandle()
   signal.signal(signal.SIGINT, sig.sigint_handler)
   win = window(work,srcdir,destdirtree)
   sig.setwin(win)
   win.run()
   win.finishup()
