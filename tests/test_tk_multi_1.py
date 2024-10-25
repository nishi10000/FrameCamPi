# frame1.py
import tkinter as tk
import sys
import os
import logging
# main.py に追加

# srcディレクトリをPythonのパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)
from utils import get_screen_sizes, setup_logging, load_config
from photoframe_tkinter import PhotoFrame

# frame1.py
import tkinter as tk

class Frame1(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = tk.Label(self, text="これはFrame1です")
        label.pack(pady=10)
        
        instruction = tk.Label(self, text="A: 前の画面, D: 次の画面")
        instruction.pack(pady=5)
        
        # Frame2へ切り替えボタン（重複を削除）
        frame2_button = tk.Button(self, text="Frame2へ切り替え",
                                  command=lambda: controller.show_frame("Frame2"))
        frame2_button.pack()
        
        # PhotoFrameへ切り替えるボタンを追加
        photo_button = tk.Button(self, text="フォトフレームへ",
                                 command=lambda: controller.show_frame("PhotoFrame"))
        photo_button.pack()





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


class MainApp(tk.Tk):
    def __init__(self, config):
        super().__init__()
        
        # フルスクリーン設定（ここで一括管理）
        self.attributes('-fullscreen', True)
        logging.debug("ウィンドウをフルスクリーンに設定しました。")
        
        # Escapeキーで終了
        self.bind("<Escape>", lambda e: self.destroy())
        logging.debug("Escapeキーをバインドしました。")
        
        # コンテナの作成
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # フレームを保持する辞書
        self.frames = {}
        # フレームの順序を定義
        self.frame_order = ["Frame1", "Frame2", "PhotoFrame"]
        self.current_frame_index = 0
        
        # フォトフレームの設定を取得
        photo_directory = config['slideshow']['photos_directory']
        interval = config['slideshow']['interval']
        
        # フレームの作成と保存
        for F in (Frame1, Frame2, lambda parent, controller: PhotoFrame(parent, photo_directory, interval)):
            frame_name = F.__name__ if hasattr(F, '__name__') else "PhotoFrame"
            frame = F(parent=container, controller=self)
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        
        # PhotoFrame の追加
        photo_frame = PhotoFrame(parent=container, photo_directory=photo_directory, interval=interval, controller=self)
        frame_name = "PhotoFrame"
        self.frames[frame_name] = photo_frame
        photo_frame.grid(row=0, column=0, sticky="nsew")
        
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
        logging.debug(f"現在のフレーム: {frame_name}")
    
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
    # スクリプトのディレクトリを取得
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
    src_dir = os.path.join(parent_dir, 'src')
    sys.path.insert(0, src_dir)
    
    # ログ設定を初期化
    setup_logging(src_dir)
    logging.debug("ログ設定を初期化しました。")
    
    # config.yaml のパスを指定
    config_path = os.path.join(src_dir, 'config.yaml')
    
    # 設定ファイルを読み込む
    config = load_config(config_path)
    if config is None:
        logging.error("設定ファイルの読み込みに失敗しました。アプリケーションを終了します。")
        exit(1)
    
    # スライドショーの設定を取得
    try:
        photo_directory = config['slideshow']['photos_directory']
        interval = config['slideshow']['interval']
        logging.debug(f"フォトディレクトリ: {photo_directory}")
        logging.debug(f"スライドショーの間隔: {interval} ミリ秒")
    except KeyError as e:
        logging.error(f"設定ファイルに必要なキーが不足しています: {e}")
        exit(1)
    
    get_screen_sizes()
    
    # MainApp のインスタンス化時に config を渡す
    app = MainApp(config)
    app.title("フレーム切り替えデモ")
    app.mainloop()
