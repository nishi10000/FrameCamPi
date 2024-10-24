import tkinter as tk 
import sys
import os
# srcディレクトリをPythonのパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)
from utils import get_screen_sizes

class View(tk.Frame): 
    
    def __init__(self,master=None, *args, **kwargs): 
        self.master = master
        self.count = 0
        super().__init__(master)
        self.pack()
        b = tk.Button(self, text="Open new window", command=self.new_window) 
        b.pack(side="top", fill="both", padx=10, pady=10) 
 
    def new_window(self): 
       self.count += 1 
       id = "New window #{}".format(self.count) 
       window = tk.Toplevel(self) 
       label = tk.Label(window, text=id) 
       label.pack(side="top", fill="both", padx=10, pady=10) 
 
if __name__ == "__main__": 
    get_screen_sizes()
    root = tk.Tk() 
    root.geometry("200x100")
    view = View(root) 
    view.mainloop() 
