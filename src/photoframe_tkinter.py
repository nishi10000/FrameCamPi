import tkinter as tk
from PIL import Image, ImageTk
import os
from screeninfo import get_monitors
import logging

# ログの設定
logging.basicConfig(
    filename='/home/sini/work/FrameCamPi/src/debug.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(message)s'
)

def get_screen_sizes():
    monitors = get_monitors()
    for monitor in monitors:
        logging.debug(f"ディスプレイ {monitor.name}: 幅={monitor.width}, 高さ={monitor.height}")
        print(f"ディスプレイ {monitor.name}: 幅={monitor.width}, 高さ={monitor.height}")

class PhotoFrame(tk.Tk):
    def __init__(self, photo_directory, interval=5000):
        super().__init__()
        self.photo_directory = photo_directory
        self.interval = interval  # ミリ秒
        self.photos = self.load_photos()
        self.current = 0

        # 実際の画面サイズをTkinterから取得
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        print(f"実際の画面サイズを取得しました: {screen_width}x{screen_height}")
        logging.debug(f"実際の画面サイズを取得しました: {screen_width}x{screen_height}")

        # フルスクリーン設定
        self.attributes('-fullscreen', True)
        print("ウィンドウをフルスクリーンに設定しました。")
        logging.debug("ウィンドウをフルスクリーンに設定しました。")

        # ウィンドウの更新を行い、サイズを確定
        self.update()
        print("ウィンドウを更新しました。")
        logging.debug("ウィンドウを更新しました。")

        # Canvasの作成とパッキング
        self.canvas = tk.Canvas(self, bg='black', highlightthickness=0, width=screen_width, height=screen_height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        print(f"Canvasを作成し、ウィンドウにパックしました。 サイズ: {screen_width}x{screen_height}")
        logging.debug(f"Canvasを作成し、ウィンドウにパックしました。 サイズ: {screen_width}x{screen_height}")

        # Canvasのサイズを取得（確認用）
        self.update_idletasks()  # Canvasのサイズを確定
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        print(f"Canvasのサイズ: {canvas_width}x{canvas_height}")
        logging.debug(f"Canvasのサイズ: {canvas_width}x{canvas_height}")

        # イベントバインド
        self.bind("<Escape>", lambda e: self.destroy())  # Escapeキーで終了
        print("Escapeキーをバインドしました。")
        logging.debug("Escapeキーをバインドしました。")

        # 黒い背景画像を作成
        self.background = self.create_black_background(screen_width, screen_height)

        # 写真表示開始
        self.show_photo()

    def load_photos(self):
        supported_formats = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
        if not os.path.exists(self.photo_directory):
            print(f"指定されたフォトディレクトリが存在しません: {self.photo_directory}")
            logging.error(f"指定されたフォトディレクトリが存在しません: {self.photo_directory}")
            self.destroy()
            return []
        photos = [os.path.join(self.photo_directory, f) for f in os.listdir(self.photo_directory) if f.lower().endswith(supported_formats)]
        print(f"読み込まれた写真の数: {len(photos)}")
        logging.debug(f"読み込まれた写真の数: {len(photos)}")
        return photos

    def create_black_background(self, screen_width, screen_height):
        # 黒い画像を作成
        black_image = Image.new('RGB', (screen_width, screen_height), (0, 0, 0))
        self.background_photo = ImageTk.PhotoImage(black_image)
        print("黒い背景画像を作成しました。")
        logging.debug("黒い背景画像を作成しました。")

        # Canvasに黒い背景画像を描画
        self.canvas.create_image(0, 0, anchor='nw', image=self.background_photo)
        print("Canvasに黒い背景画像を描画しました。")
        logging.debug("Canvasに黒い背景画像を描画しました。")

        return black_image

    def show_photo(self):
        if not self.photos:
            print("写真が見つかりません。フォトディレクトリに画像を追加してください。")
            logging.warning("写真が見つかりません。フォトディレクトリに画像を追加してください。")
            self.destroy()
            return

        photo_path = self.photos[self.current]
        print(f"次に表示する写真のパス: {photo_path}")
        logging.debug(f"次に表示する写真のパス: {photo_path}")

        try:
            img = Image.open(photo_path)
            print(f"写真を開きました: {photo_path} (元のサイズ: {img.size})")
            logging.debug(f"写真を開きました: {photo_path} (元のサイズ: {img.size})")

            # 画面サイズを取得（Tkinterから）
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            print(f"再度画面サイズを取得しました: {screen_width}x{screen_height}")
            logging.debug(f"再度画面サイズを取得しました: {screen_width}x{screen_height}")

            # 画像の元のサイズを取得
            img_width, img_height = img.size

            # スケーリングファクターを計算
            scale_w = screen_width / img_width
            scale_h = screen_height / img_height
            scale = min(scale_w, scale_h)
            print(f"スケーリングファクター: 幅={scale_w}, 高さ={scale_h}, 使用スケール={scale}")
            logging.debug(f"スケーリングファクター: 幅={scale_w}, 高さ={scale_h}, 使用スケール={scale}")

            # 新しいサイズを計算
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            print(f"リサイズ後の画像サイズ: {new_width}x{new_height}")
            logging.debug(f"リサイズ後の画像サイズ: {new_width}x{new_height}")

            # 画像をリサイズ（Resamplingを使用せずに直接フィルターを指定）
            img = img.resize((new_width, new_height), Image.LANCZOS)  # DeprecationWarningあり
            print("画像をリサイズしました。")
            logging.debug("画像をリサイズしました。")

            # Tkinter用のPhotoImageに変換
            photo = ImageTk.PhotoImage(img)
            print("PhotoImageに変換しました。")
            logging.debug("PhotoImageに変換しました。")

            # Canvas上の既存の画像を削除
            self.canvas.delete("all")
            print("Canvas上の既存の画像を削除しました。")
            logging.debug("Canvas上の既存の画像を削除しました。")

            # 黒い背景画像を再描画
            self.canvas.create_image(0, 0, anchor='nw', image=self.background_photo)
            print("Canvasに黒い背景画像を再描画しました。")
            logging.debug("Canvasに黒い背景画像を再描画しました。")

            # 画像を中央に配置
            x_center = screen_width // 2
            y_center = screen_height // 2
            self.canvas.create_image(x_center, y_center, image=photo, anchor='center')
            self.canvas.image = photo  # 参照を保持
            print(f"画像をCanvasの中央に配置しました: ({x_center}, {y_center})")
            logging.debug(f"画像をCanvasの中央に配置しました: ({x_center}, {y_center})")

        except Exception as e:
            print(f"写真の読み込み中にエラーが発生しました: {e}")
            logging.error(f"写真の読み込み中にエラーが発生しました: {e}")

        self.current = (self.current + 1) % len(self.photos)
        print(f"次の写真に切り替えます: インデックス={self.current}")
        logging.debug(f"次の写真に切り替えます: インデックス={self.current}")

        self.after(self.interval, self.show_photo)

# テスト用の実行例
if __name__ == "__main__":
    from utils import load_config

    if os.environ.get('DISPLAY', '') == '':
        print('no display found. Using :0.0')
        logging.debug('no display found. Using :0.0')
        os.environ['DISPLAY'] = ':0.0'
        os.environ['XAUTHORITY'] = '/home/sini/.Xauthority'
        print("DISPLAY環境変数を ':0.0' に設定しました。")
        logging.debug("DISPLAY環境変数を ':0.0' に設定しました。")

    # config.yaml のパスを正しく指定
    config = load_config('config.yaml')  # srcディレクトリ内で実行する場合
    photo_directory = config['slideshow']['photos_directory']
    interval = config['slideshow']['interval']
    print(f"フォトディレクトリ: {photo_directory}")
    logging.debug(f"フォトディレクトリ: {photo_directory}")
    print(f"スライドショーの間隔: {interval} ミリ秒")
    logging.debug(f"スライドショーの間隔: {interval} ミリ秒")

    app = PhotoFrame(photo_directory, interval)
    get_screen_sizes()
    app.mainloop()
