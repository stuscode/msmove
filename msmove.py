#!/usr/bin/env python3

import argparse
import tkinter as tk
from tkinter import ttk
import threading
import time
import queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
 
class window(tk.Tk):
   def __init__(self, workqueue):
      super().__init__()
      self.work = workqueue
      self.wm_title("msmove")
      self.dobutton = ttk.Button(self, text="Move",command=self.doit)
      self.dobutton.grid(row=0,column=0)
      self.cancelbutton = ttk.Button(self, text="Cancel",command=self.destroywin)
      self.cancelbutton.grid(row=0,column=1)
#self.name = self.getwork()
      self.workget = threading.Thread(target=self.getworkthread, args=(self,))
      self.movedone = threading.Condition



   def doit(self):
      print("process ",self.name)
      self.movedone.notify()

   def getworkthread(self):
      while True:
         self.name = self.work.get()
         print("set filename to ",self.name)
         self.movedone.wait()

   def getwork(self):
      name = None
      try:
         name = self.work.get(block = False)
         print("got ",name)
      except queue.Empty:
         print("destroy")
#self.destroywin()
      print("getwork", name)
      return name
   #TODO: if there is no work, leave window up
#also: have mode where window starts up so defaults can be edited
   def destroywin(self):
      self.destroy()
 
class wincontrol:
   def __init__(self, dir, workqueue):
      self.watchdir = dir
      self.work = workqueue
      self.observer = Observer()
 
   def run(self):
          #set up handler
      event_handler = eventhandle()
      event_handler.setqueue(self.work)
      self.observer.schedule(event_handler, self.watchdir, recursive = True)
      self.observer.start()
       #process work
      try:
         while True: 
#name = self.work.get()  #wait for work
#            print("got work 1 ", name)
#            self.work.put(name) #put it back for processing
            win = window(work)
            win.lift() #maybe
            win.attributes('-topmost', True) #mayb
            win.mainloop()
      except Exception as e:
         print(e)
         self.observer.stop()
         print("Observer Stopped")
 
      self.observer.join()
 
class eventhandle(FileSystemEventHandler):
   work = None
   def setqueue(self, queue):
      work = queue

   @staticmethod
   def on_moved(event):
          #this is the move after the browser finishes download
      dest = event.dest_path
      if dest.endswith('.pdf') or dest.endswith('.PDF'):  
         work.put(dest)
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
#winthread = threading.Thread(target=wincontrol, args=(work,))
#workthread = threading.Thread(target=workget, args=(work,))
   watch = wincontrol(srcdir, work)
   watch.run()

