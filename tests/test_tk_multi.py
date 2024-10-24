# frame1.py
import tkinter as tk
import sys
import os
# srcディレクトリをPythonのパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)
from utils import get_screen_sizes

# frame1.py
import tkinter as tk

class Frame1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        label = tk.Label(self, text="これはFrame1です")
        label.pack(pady=10)
        
        instruction = tk.Label(self, text="A: 前の画面, D: 次の画面")
        instruction.pack(pady=5)
        
        button = tk.Button(self, text="Frame2へ切り替え",
                          command=lambda: controller.show_frame("Frame2"))
        button.pack()

# frame2.py
class Frame2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        label = tk.Label(self, text="これはFrame2です")
        label.pack(pady=10)
        
        instruction = tk.Label(self, text="A: 前の画面, D: 次の画面")
        instruction.pack(pady=5)
        
        button = tk.Button(self, text="Frame1へ切り替え",
                          command=lambda: controller.show_frame("Frame1"))
        button.pack()

# main.py
class MainApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        # コンテナの作成
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # フレームを保持する辞書
        self.frames = {}
        # フレームの順序を定義
        self.frame_order = ["Frame1", "Frame2"]
        self.current_frame_index = 0
        
        # フレームの作成と保存
        for F in (Frame1, Frame2):
            frame_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # キーバインドの設定
        self.bind('<a>', self.show_previous_frame)  # 小文字のa
        self.bind('<A>', self.show_previous_frame)  # 大文字のA
        self.bind('<d>', self.show_next_frame)      # 小文字のd
        self.bind('<D>', self.show_next_frame)      # 大文字のD
        
        # 最初に表示するフレーム
        self.show_frame("Frame1")
    
    def show_frame(self, frame_name):
        """指定されたフレームを前面に表示"""
        frame = self.frames[frame_name]
        frame.tkraise()
        # 現在のフレームインデックスを更新
        self.current_frame_index = self.frame_order.index(frame_name)
    
    def show_next_frame(self, event=None):
        """Dキーで次のフレームを表示"""
        next_index = (self.current_frame_index + 1) % len(self.frame_order)
        next_frame = self.frame_order[next_index]
        self.show_frame(next_frame)
    
    def show_previous_frame(self, event=None):
        """Aキーで前のフレームを表示"""
        prev_index = (self.current_frame_index - 1) % len(self.frame_order)
        prev_frame = self.frame_order[prev_index]
        self.show_frame(prev_frame)

if __name__ == "__main__":
    get_screen_sizes()
    app = MainApp()
    app.geometry("400x300")
    app.title("フレーム切り替えデモ")
    app.mainloop()