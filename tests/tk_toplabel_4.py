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

class View(tk.Frame):
    def __init__(self, master=None, camera_handler=None, photo_directory=None, interval=5000, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.camera_handler = camera_handler
        self.photo_directory = photo_directory
        self.interval = interval
        self.count = 0
        self.pack(fill=tk.BOTH, expand=True)
        self.current_frame = None  # 現在のフレームを保持

        # コンテナフレームを作成
        self.container = tk.Frame(self.master)
        self.container.pack(fill=tk.BOTH, expand=True)

    def open_mode_window(self, selected_mode):
        if not selected_mode:
            logging.warning("モードが選択されていません。")
            messagebox.showwarning("警告", "モードが選択されていません。")
            return

        self.count += 1

        # 現在のフレームを削除
        if self.current_frame:
            self.current_frame.destroy()

        # 選択されたモードに応じてフレームを作成
        if selected_mode == "smile_detection":
            self.current_frame = SmileDetectionFrame(self.container, self.camera_handler)
        elif selected_mode == "photo_slideshow":
            self.current_frame = PhotoFrame(self.container, photo_directory=self.photo_directory, interval=self.interval, controller=None)
        else:
            logging.error(f"未対応のモードが選択されました: {selected_mode}")
            messagebox.showerror("エラー", f"未対応のモードが選択されました: {selected_mode}")
            return

        if self.current_frame:
            self.current_frame.pack(fill=tk.BOTH, expand=True)

def main():
    # ログ設定を初期化
    setup_logging(src_dir, log_file='smile_detection.log')
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

    # Tkinter アプリケーションを初期化
    root = tk.Tk()
    root.title("Smile Detection App")

    # 全画面表示に設定
    root.attributes('-fullscreen', True)

    # View クラスのインスタンスを作成し、カメラハンドラーとスライドショー設定を渡す
    view = View(root, camera_handler=camera_handler, photo_directory=photo_directory, interval=interval)
    view.pack(fill=tk.BOTH, expand=True)

    # キーボードイベントのバインド
    root.bind("<Escape>", lambda e: root.destroy())  # Escapeキーで終了

    # モード変更用の関数
    def change_mode(mode):
        view.open_mode_window(mode)

    # キーボードイベントのバインド
    root.bind("1", lambda e: change_mode("smile_detection"))  # 1キーでモードを変更
    root.bind("2", lambda e: change_mode("photo_slideshow"))  # 2キーでモードを変更

    # デフォルトのモードを設定
    view.open_mode_window("smile_detection")

    # Tkinter のメインループを開始
    try:
        root.mainloop()
    except Exception as e:
        logging.error(f"アプリケーションの実行中にエラーが発生しました: {e}")
        messagebox.showerror("エラー", f"アプリケーションの実行中にエラーが発生しました: {e}")
    finally:
        # リソースのクリーンアップ
        camera_handler.release_camera()
        logging.info("アプリケーションを終了しました。")

if __name__ == "__main__":
    main()