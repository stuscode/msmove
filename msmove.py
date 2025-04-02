#!/usr/bin/env python3

import tkinter as tk
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
      self.name = self.getwork()
      if self.name == None:
         self.exists = False
      else:
         self.exists = True
      print(self.name)
 
class wincontrol:
    def __init__(self, dir, workqueue):
        self.watchdir = dir
        self.work = workqueue
        self.observer = Observer()
 
    def run(self):
          #set up handler
        event_handler = changehandle()
        self.observer.schedule(event_handler, self.watchdir, recursive = True)
        self.observer.start()
          #process work
        try:
           while True:
              name = self.work.get()  #wait for work
              self.work.put() #put it back for processing
              win = window(work)
              if win.exists:
                 win.lift() #maybe
                 win.attributes('-topmost', True) #mayb
                 win.mainloop()
        except:
            self.observer.stop()
            print("Observer Stopped")
 
        self.observer.join()
 
class changehandle(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            # Event is created, you can process it now
            print("Watchdog received created event - % s." % event.src_path)
        elif event.event_type == 'moved':
            # Event is modified, you can process it now
            print("Watchdog received moved event - % s % s." % (event.src_path,event.dest_path))
             

def arguments():
   p = argparse.ArgumentParser(description="move monthly statements")
   p.add_argument('srcdir')
   p.add_argument('destdirtree')
   args = p.parse_args();
   return(args.srcdir, args.destdirtree)
 
if __name__ == '__main__':
        #process command line arguments
   (srcdir, destdirtree) = arguments()
   work = queue.Queue
   winthread = threading.Thread(target=wincontrol, args=(work,))
   workthread = threading.Thread(target=workget, args=(work,))
    watch = wincontrol('.')
    watch.run()

