# photoframe_tkinter.py: Tkinterを使用してフォトフレーム表示機能を提供するモジュール
# src/photoframe_tkinter.py

import tkinter as tk
from PIL import Image, ImageTk
import os
import time

class PhotoFrame(tk.Tk):
    def __init__(self, photo_directory, interval=5000):
        super().__init__()
        self.photo_directory = photo_directory
        self.interval = interval  # ミリ秒
        self.photos = self.load_photos()
        self.current = 0

        self.label = tk.Label(self)
        self.label.pack(expand=True)

        self.bind("<Escape>", lambda e: self.destroy())  # Escapeキーで終了
        self.attributes('-fullscreen', True)  # フルスクリーン表示

        self.show_photo()
    
    def load_photos(self):
        supported_formats = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
        if not os.path.exists(self.photo_directory):
            print(f"指定されたフォトディレクトリが存在しません: {self.photo_directory}")
            self.destroy()
            return []
        return [os.path.join(self.photo_directory, f) for f in os.listdir(self.photo_directory) if f.lower().endswith(supported_formats)]
    
    def show_photo(self):
        if not self.photos:
            print("写真が見つかりません。フォトディレクトリに画像を追加してください。")
            self.destroy()
            return
        
        photo_path = self.photos[self.current]
        try:
            img = Image.open(photo_path)
            img = img.resize((self.winfo_screenwidth(), self.winfo_screenheight()), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(img)
            self.label.config(image=photo)
            self.label.image = photo  # 参照を保持
            print(f"表示中の写真: {photo_path}")
        except Exception as e:
            print(f"写真の読み込み中にエラーが発生しました: {e}")
        
        self.current = (self.current + 1) % len(self.photos)
        self.after(self.interval, self.show_photo)

# テスト用の実行例
if __name__ == "__main__":
    from utils import load_config

    if os.environ.get('DISPLAY','') == '':
        print('no display found. Using :0.0')
        os.environ.__setitem__('DISPLAY', ':0.0')

    # config.yaml のパスを正しく指定
    config = load_config('config.yaml')  # srcディレクトリ内で実行する場合
    photo_directory = config['slideshow']['photos_directory']
    interval = config['slideshow']['interval']
    print(photo_directory)
    app = PhotoFrame(photo_directory, interval)
    app.mainloop()
