import tkinter as tk
import sys
import os
import logging
import tkinter.messagebox as messagebox  # エラーメッセージ表示用

# srcディレクトリをPythonのパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

from utils import get_screen_sizes, load_config, setup_logging
from smile_detection import SmileDetectionFrame, SmileDetectionCameraHandler
from photoframe_tkinter import PhotoFrame

class Application(tk.Tk):
    def __init__(self, camera_handler, photo_directory, interval, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Smile Detection App")
        self.fullscreen = True  # フルスクリーン状態を管理
        self.attributes('-fullscreen', self.fullscreen)
        self.camera_handler = camera_handler
        self.photo_directory = photo_directory
        self.interval = interval
        self.current_frame = None  # 現在のフレームを保持

        # モードの初期化
        self.modes = {
            "smile_detection": SmileDetectionFrame,
            "photo_slideshow": PhotoFrame
        }
        self.current_mode = None

        # コンテナフレームを作成
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        # キーボードイベントのバインド
        self.bind("<Escape>", self.toggle_fullscreen)  # Escapeキーでフルスクリーンをトグル
        self.bind("q", lambda e: self.destroy())  # 'q'キーで終了
        self.bind("1", lambda e: self.change_mode("smile_detection"))  # '1'キーで撮影モードに変更
        self.bind("2", lambda e: self.change_mode("photo_slideshow"))  # '2'キーでフォトモードに変更

        # デフォルトのモードを設定
        self.change_mode("smile_detection")

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.attributes('-fullscreen', self.fullscreen)
        logging.info(f"フルスクリーンを {'有効化' if self.fullscreen else '無効化'} しました。")

    def change_mode(self, mode_name):
        if mode_name not in self.modes:
            logging.error(f"未対応のモードが選択されました: {mode_name}")
            messagebox.showerror("エラー", f"未対応のモードが選択されました: {mode_name}")
            return

        # 現在のフレームを削除
        if self.current_frame is not None:
            self.current_frame.destroy()
            logging.debug(f"前のモード '{self.current_mode}' を終了しました。")

        # 新しいモードのフレームを作成
        FrameClass = self.modes[mode_name]
        if mode_name == "smile_detection":
            self.current_frame = FrameClass(self.container, self.camera_handler)
        elif mode_name == "photo_slideshow":
            self.current_frame = FrameClass(
                self.container,
                photo_directory=self.photo_directory,
                interval=self.interval,
                controller=None
            )
        else:
            logging.error(f"モード '{mode_name}' のフレームを作成できませんでした。")
            return

        self.current_frame.pack(fill=tk.BOTH, expand=True)
        self.current_mode = mode_name
        logging.info(f"モードを '{mode_name}' に切り替えました。")

    def destroy(self):
        # リソースのクリーンアップ
        if self.camera_handler:
            self.camera_handler.release_camera()
            logging.info("カメラをリリースしました。")

        # 現在のフレームを破棄
        if self.current_frame:
            self.current_frame.destroy()
            logging.debug(f"フレーム '{self.current_mode}' を破棄しました。")

        # ウィンドウを閉じる
        super().destroy()

def main():
    # ログ設定を初期化
    setup_logging(src_dir, log_file='application.log')
    logging.debug("ログ設定を初期化しました。")

    # config.yaml のパスを指定
    config_path = os.path.join(src_dir, 'config.yaml')

    # 設定ファイルを読み込む
    config = load_config(config_path)
    if config is None:
        logging.error("設定ファイルの読み込みに失敗しました。アプリケーションを終了します。")
        messagebox.showerror("エラー", "設定ファイルの読み込みに失敗しました。アプリケーションを終了します。")
        sys.exit(1)

    # スライドショーの設定を取得
    try:
        photo_directory = config['slideshow']['photos_directory']
        interval = config['slideshow']['interval']
        logging.debug(f"フォトディレクトリ: {photo_directory}")
        logging.debug(f"スライドショーの間隔: {interval} ミリ秒")
    except KeyError as e:
        logging.error(f"設定ファイルに必要なキーが不足しています: {e}")
        messagebox.showerror("エラー", f"設定ファイルに必要なキーが不足しています: {e}")
        sys.exit(1)

    # 写真保存ディレクトリを取得
    photo_directory = os.path.join(src_dir, photo_directory)

    # ディレクトリが存在しない場合は作成
    try:
        os.makedirs(photo_directory, exist_ok=True)
        logging.info(f"写真保存ディレクトリ: {photo_directory}")
    except Exception as e:
        logging.error(f"写真保存ディレクトリの作成に失敗しました: {e}")
        messagebox.showerror("エラー", f"写真保存ディレクトリの作成に失敗しました: {e}")
        sys.exit(1)

    # カメラハンドラーのインスタンスを作成
    camera_config = config.get('camera', {})
    try:
        camera_handler = SmileDetectionCameraHandler(
            camera_index=camera_config.get('index', 0),
            countdown_time=camera_config.get('countdown_time', 3),
            preview_time=camera_config.get('preview_time', 3),
            photo_directory=photo_directory
        )
    except Exception as e:
        logging.error(f"カメラハンドラーの初期化に失敗しました: {e}")
        messagebox.showerror("エラー", f"カメラハンドラーの初期化に失敗しました: {e}")
        sys.exit(1)

     # アプリケーションを初期化
    app = Application(camera_handler, photo_directory, interval)

    # メインループを開始
    try:
        app.mainloop()
    except Exception as e:
        logging.error(f"アプリケーションの実行中にエラーが発生しました: {e}")
        messagebox.showerror("エラー", f"アプリケーションの実行中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()