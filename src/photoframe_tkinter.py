# photoframe_tkinter.py

import tkinter as tk
from PIL import Image, ImageTk
import os
import logging
from utils import get_screen_sizes, setup_logging, load_config

class PhotoFrame(tk.Frame):
    def __init__(self, parent, photo_directory, interval=5000, controller=None):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller  # コントローラーを保持
        self.photo_directory = photo_directory
        self.interval = interval  # ミリ秒
        self.photos = self.load_photos()
        self.current = 0

        # トップレベルウィンドウを取得
        self.top_level = self.winfo_toplevel()

        # 実際の画面サイズをTkinterから取得
        screen_width = self.top_level.winfo_screenwidth()
        screen_height = self.top_level.winfo_screenheight()
        logging.debug(f"実際の画面サイズを取得しました: {screen_width}x{screen_height}")

        # フルスクリーン設定
        self.top_level.attributes('-fullscreen', True)
        logging.debug("ウィンドウをフルスクリーンに設定しました。")

        # Canvasの作成とパッキング
        self.canvas = tk.Canvas(self, bg='black', highlightthickness=0, width=screen_width, height=screen_height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        logging.debug(f"Canvasを作成し、フレームにパックしました。 サイズ: {screen_width}x{screen_height}")

        # Canvasのサイズを取得（確認用）
        self.update_idletasks()  # Canvasのサイズを確定
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        logging.debug(f"Canvasのサイズ: {canvas_width}x{canvas_height}")

        # イベントバインド
        self.top_level.bind("<Escape>", self.exit_fullscreen)
        logging.debug("Escapeキーをバインドしました。")

        # 黒い背景画像を作成
        self.background = self.create_black_background(screen_width, screen_height)

        # 写真表示開始
        self.show_photo()

    def exit_fullscreen(self, event=None):
        self.top_level.attributes('-fullscreen', False)
        if self.controller:
            self.controller.show_frame("MainMenu")

    def destroy(self):
        # スライドショーの更新を停止
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
            logging.debug("スライドショーの更新を停止しました。")
        # スーパークラスの destroy を呼び出す
        super().destroy()

    def load_photos(self):
        supported_formats = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
        if not os.path.exists(self.photo_directory):
            print(f"指定されたフォトディレクトリが存在しません: {self.photo_directory}")
            logging.error(f"指定されたフォトディレクトリが存在しません: {self.photo_directory}")
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
            self.parent.destroy()
            return

        photo_path = self.photos[self.current]
        print(f"次に表示する写真のパス: {photo_path}")
        logging.debug(f"次に表示する写真のパス: {photo_path}")

        try:
            img = Image.open(photo_path)
            print(f"写真を開きました: {photo_path} (元のサイズ: {img.size})")
            logging.debug(f"写真を開きました: {photo_path} (元のサイズ: {img.size})")

            # 画面サイズを取得（Tkinterから）
            screen_width = self.parent.winfo_screenwidth()
            screen_height = self.parent.winfo_screenheight()
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
    def test_photo_frame():
        # スクリプトのディレクトリを取得
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # ログ設定を初期化
        setup_logging(script_dir)
        logging.debug("ログ設定を初期化しました。")

        # config.yaml のパスを指定
        config_path = os.path.join(script_dir, 'config.yaml')

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

        # 画面サイズを取得（必要に応じて使用）
        get_screen_sizes()

        # Tkinterのルートウィンドウを作成
        root = tk.Tk()
        root.withdraw()  # 一旦非表示にする

        # PhotoFrameをメインフレームとして配置
        app = PhotoFrame(root, photo_directory, interval)
        app.pack(fill=tk.BOTH, expand=True)
        root.deiconify()  # ルートウィンドウを表示

        # メインループを開始
        try:
            root.mainloop()
        except Exception as e:
            logging.error(f"アプリケーションの実行中にエラーが発生しました: {e}")
            exit(1)

    test_photo_frame()
