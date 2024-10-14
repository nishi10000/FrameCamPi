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
            
            # 画面サイズを取得
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            
            # 画像の元のサイズを取得
            img_width, img_height = img.size
            
            # スケーリングファクターを計算
            scale_w = screen_width / img_width
            scale_h = screen_height / img_height
            scale = min(scale_w, scale_h)
            
            # 新しいサイズを計算
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # 画像をリサイズ
            img = img.resize((new_width, new_height), Image.ANTIALIAS)
            
            # Tkinter用のPhotoImageに変換
            photo = ImageTk.PhotoImage(img)
            
            # 画像をラベルに設定
            self.label.config(image=photo)
            self.label.image = photo  # 参照を保持
            
            print(f"表示中の写真: {photo_path} (サイズ: {new_width}x{new_height})")
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
