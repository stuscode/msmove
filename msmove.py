#!/usr/bin/env python3

import argparse
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
 
class window(tk.Tk):
   def __init__(self, workqueue, srcdir, destdirtree):
      super().__init__()
      self.work = workqueue
      self.observer = None
      self.srcdir = srcdir
      self.destdirtree = destdirtree
      self.endqueue = False

   def wincreate(self):
      row = 0
      self.wm_title("msmove")
      self.grid_columnconfigure(2, weight=1)
      self.srclabel = Label(self, text="source:")
      self.srclabel.grid(row=row, column= 0)
      self.srcname = Label(self, width=40)
      self.srcname.grid(row=row, column=1)
      self.cancelbutton = Button(self, text="Exit",command=self.destroywin)
      self.cancelbutton.grid(row=row,column=2)
      row = row + 1
      self.destlabel = Label(self, text="dest:")
      self.destlabel.grid(row=row, column= 0)
      self.destnamevar = tk.StringVar()
      self.destname = Entry(self, width=40, textvar=self.destnamevar)
      self.destname.grid(row=row, column=1)
      self.dobutton = Button(self, text="Move",command=self.doit)
      self.dobutton.grid(row=row,column=2)
      row = row + 1
      self.sep1 = ttk.Separator(self,orient=tk.HORIZONTAL)
      self.sep1.grid(row=row, column=0, columnspan=4, sticky='ew')
      row = row + 1
      self.srcdirlab = Label(self, text="source dir:")
      self.srcdirlab.grid(row=row, column=0)
      self.srcdirdis = Label(self, text=srcdir)
      self.srcdirdis.grid(row=row, column=1)
      self.srcdirsel = Button(self, text="Sel",command=self.picsrcdir)
      self.srcdirsel.grid(row=row, column=2)
      row = row + 1
      self.sep1 = ttk.Separator(self,orient=tk.HORIZONTAL)
      self.sep1.grid(row=row, column=0, columnspan=4, sticky='ew')
      row = row + 1
      self.dstdirlab = Label(self, text="dest dirs:")
      self.dstdirlab.grid(row=row, column=0)
      self.dstdirdis = Label(self,width=40, text=self.destdirtree)
      self.dstdirdis.grid(row=row, column=1)
      self.dstdirsel = Button(self, text="Sel",command=self.picdstdir)
      self.dstdirsel.grid(row=row, column=2)
      row = row + 1
      self.sep1 = ttk.Separator(self,orient=tk.HORIZONTAL)
      self.sep1.grid(row=row, column=0, columnspan=4, sticky='ew')
      row = row + 1
#self.dirlist=scrolledtext.ScrolledText(self,width=50,height=20)
      self.dirlist=dirlistpanel(self)
      self.dirlist.grid(row=row,column=0,columnspan=4)
      row = row + 1

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

   def setdirlist(self):
      self.dirlist.settopdir(self.destdirtree)

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

   def doit(self):
      print("process ",self.name)

   def getworkthread(self):
      while True:
         self.name = self.work.get()
         if self.endqueue:
            break
         print("set filename to ",self.name)
         self.srcname.config(text=os.path.basename(self.name))
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


class dirlistpanel(scrolledtext.ScrolledText):
   def __init__(self, c):
      super().__init__(c, width=50,height=20)
      self.bind("<Key>",self.dirlistkey)
      self.bind("<Button-1>",self.dirlistclick)
      self.bind("<B1-Motion>",self.dirlistclick)

   def dirlistkey(self,event):
      print("here")
      return "break"

   def dirlistclick(self,event):
      print("here")
      return "break"

   def settopdir(self, topdir):
      self.topdir = topdir
      subfolders = [ f.name for f in os.scandir(topdir) if f.is_dir() ]



class destdirlist():
   def setdirs(self, dirlist):
      self.dirs = dirlist
   def getdirs(self):
      return self.dirs

class destdir():
   def set(self, name, pattern, newname):
      self.name = name
      self.pattern = pattern
      self.renamepattern = newname



class eventhandle(watchdog.events.FileSystemEventHandler):
   work = None
   def setqueue(self, queue):
      self.work = queue

#@staticmethod
   def on_moved(self, event):
          #this is the move after the browser finishes download
      dest = event.dest_path
      if dest.endswith('.pdf') or dest.endswith('.PDF'):  
         self.work.put(dest)
      print(event.src_path, event.dest_path);


class sighandle():
   win = None

   def setwin(self,window):
      self.win = window

   def sigint_handler(self, sig, frame):
      print("signal")
      self.win.finishwin()
      self.win.finishup()

def arguments():
   p = argparse.ArgumentParser(description="move monthly statements")
   p.add_argument('srcdir')
   p.add_argument('destdirtree')
   args = p.parse_args();
   return(args.srcdir, args.destdirtree)
 
def wthread(work,srcdir,destdirtree,sig):
   win = window(work,srcdir,destdirtree) #when this returns we are done
   sig.setwin(win)
   win.run()
   win.finishup()

if __name__ == '__main__':
   global win
        #process command line arguments
   (srcdir, destdirtree) = arguments()
   work = queue.Queue()

   sig = sighandle()
   signal.signal(signal.SIGINT, sig.sigint_handler)
   #winthread = threading.Thread(target=wthread, args=(work,srcdir,sig))
   #winthread.start()
   #winthread.join()
   wthread(work,srcdir,destdirtree,sig)


