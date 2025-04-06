#!/usr/bin/env python3

import argparse
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import *
import threading
import time
import queue
import watchdog.events
import watchdog.observers
 
class window(tk.Tk):
   def __init__(self, workqueue):
      super().__init__()
      row = 0
      self.work = workqueue
      self.observer == None

      self.wm_title("msmove")
      self.grid_columnconfigure(2, weight=1)
      self.srclabel = Label(self, text="source:")
      self.srclabel.grid(row=row, column= 0)
      self.srcname = Label(self, width=40)
      self.srcname.grid(row=row, column=1)
      row = row + 1
      self.destlabel = Label(self, text="dest:")
      self.destlabel.grid(row=row, column= 0)
      self.destname = Entry(self, width=40)
      self.destname.grid(row=row, column=1)
      self.dobutton = Button(self, text="Move",command=self.doit)
      self.dobutton.grid(row=row,column=2)
      row = row + 1
      self.sep1 = ttk.Separator(self,orient=tk.HORIZONTAL)
      self.sep1.grid(row=row, column=0, columnspan=4, sticky='ew')
      row = row + 1
      self.srctextvar = tk.StringVar()
      self.srcdirlab = Label(self, text="source dir:")
      self.srcdirlab.grid(row=row, column=0)
      self.srcdirdis = Entry(self,width=40, textvar = self.srctextvar)
      self.srcdirdis.grid(row=row, column=1)
      self.srcdirsel = Button(self, text="Sel",command=self.picsrcdir)
      self.srcdirsel.grid(row=row, column=2)
      row = row + 1
      self.cancelbutton = Button(self, text="Exit",command=self.destroywin)
      self.cancelbutton.grid(row=row,column=1)
      row = row + 1
      self.workget = threading.Thread(target=self.getworkthread)
      self.workget.start()
      self.movedone = threading.Condition
      self.lift() #maybe
      self.attributes('-topmost', True) #maybe
      self.endqueue = False
      self.mainloop()

   def observer_restart(self):
      if self.observer != None:
         observer_end()
      self.observer = watchdog.observers.Observer()
      self.observer.schedule(event_handler, srcdir, recursive = False)
      self.observer.start()

   def observer_end(self):
      observer.stop()
      observer.join()

   def picsrcdir(self):
      newdir = filedialog.askdirectory()
      self.srctextvar.set(newdir)

   def doit(self):
      print("process ",self.name)
      self.movedone.notify()

   def getworkthread(self):
      while True:
         self.name = self.work.get()
         if self.endqueue:
            break
         print("set filename to ",self.name)
         self.lift() #maybe
         self.attributes('-topmost', True) #maybe

   def finishqueue(self):
      self.endqueue = True
      observer_end()
      work.put("")  #wake up the get so thread can exit

   def destroywin(self):
      self.destroy()

class eventhandle(watchdog.events.FileSystemEventHandler):
   work = None
   def setqueue(self, queue):
      self.work = queue

   def setwin(self, window):
      self.window = window

#@staticmethod
   def on_moved(self, event):
          #this is the move after the browser finishes download
      dest = event.dest_path
      if dest.endswith('.pdf') or dest.endswith('.PDF'):  
         self.work.put(dest)
      print(event.src_path, event.dest_path);

def arguments():
   p = argparse.ArgumentParser(description="move monthly statements")
   p.add_argument('srcdir')
   p.add_argument('destdirtree')
   args = p.parse_args();
   return(args.srcdir, args.destdirtree)
 
if __name__ == '__main__':
        #process command line arguments
   (srcdir, destdirtree) = arguments()
   work = queue.Queue()
   event_handler = eventhandle()
   event_handler.setqueue(work)

   observer = watchdog.observers.Observer()
   observer.schedule(event_handler, srcdir, recursive = False)
   observer.start()

   win = window(work) #when this returns we are done
   win.finishqueue()
   observer.stop()
   observer.join()
