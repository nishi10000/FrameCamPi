import tkinter as tk
import sys
import os
import logging
# srcディレクトリをPythonのパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)
from utils import get_screen_sizes
from smile_detection import SmileDetectionFrame,SmileDetectionCameraHandler
from photo_capture import CameraHandler
# main.py
from utils import load_config, setup_logging

class View(tk.Frame):
    def __init__(self, master=None, camera_handler=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.camera_handler = camera_handler
        self.count = 0
        self.pack(padx=20, pady=20)

        # ボタンを作成して配置
        open_button = tk.Button(self, text="Open Smile Detection Window", command=self.new_window)
        open_button.pack(side="top", fill="both", expand=True, padx=10, pady=10)

    def new_window(self):
        self.count += 1
        window_title = f"Smile Detection Window #{self.count}"
        new_window = tk.Toplevel(self.master)
        new_window.title(window_title)
        new_window.geometry("800x600")  # 必要に応じてサイズを調整

        # SmileDetectionFrameを新しいウィンドウに配置
        smile_frame = SmileDetectionFrame(new_window, self.camera_handler)
        smile_frame.pack(fill=tk.BOTH, expand=True)

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
        sys.exit(1)

    # スライドショーの設定を取得
    try:
        photo_directory = config['slideshow']['photos_directory']
        interval = config['slideshow']['interval']
        logging.debug(f"フォトディレクトリ: {photo_directory}")
        logging.debug(f"スライドショーの間隔: {interval} ミリ秒")
    except KeyError as e:
        logging.error(f"設定ファイルに必要なキーが不足しています: {e}")
        sys.exit(1)

    # 写真保存ディレクトリを取得
    photo_directory = os.path.join(src_dir, photo_directory)

    # ディレクトリが存在しない場合は作成
    try:
        os.makedirs(photo_directory, exist_ok=True)
        logging.info(f"写真保存ディレクトリ: {photo_directory}")
    except Exception as e:
        logging.error(f"写真保存ディレクトリの作成に失敗しました: {e}")
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
        sys.exit(1)

    # Tkinter アプリケーションを初期化
    root = tk.Tk()
    root.title("Smile Detection App")
    root.geometry("300x150")  # メインウィンドウのサイズを調整

    # View クラスのインスタンスを作成し、カメラハンドラーを渡す
    view = View(root, camera_handler=camera_handler)
    view.pack(fill=tk.BOTH, expand=True)

    # キーボードイベントのバインド
    root.bind("<Escape>", lambda e: root.destroy())  # Escapeキーで終了

    # ウィンドウの閉じるイベントを処理
    def on_closing():
        logging.info("アプリケーションを終了します。")
        camera_handler.release_camera()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Tkinter のメインループを開始
    try:
        root.mainloop()
    except Exception as e:
        logging.error(f"アプリケーションの実行中にエラーが発生しました: {e}")
    finally:
        # リソースのクリーンアップ
        camera_handler.release_camera()
        logging.info("アプリケーションを終了しました。")

if __name__ == "__main__":
    main()
