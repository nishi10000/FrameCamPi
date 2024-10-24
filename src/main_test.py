# main.py

import os
import logging
import tkinter as tk
from photoframe_tkinter import PhotoFrame
from smile_detection import SmileDetectionFrame
from utils import load_config, setup_logging, get_screen_sizes

class App(tk.Tk):
    def __init__(self, photo_directory, interval):
        super().__init__()
        self.photo_directory = photo_directory
        self.interval = interval
        self.title("Photo Frame & Smile Detection App")

        # フルスクリーン設定
        self.attributes('-fullscreen', True)
        logging.debug("ウィンドウをフルスクリーンに設定しました。")

        # 現在のフレームを保持する変数
        self.current_frame = None

        # 最初にPhotoFrameを表示
        self.show_photo_frame()

        # キーボードイベントのバインド
        self.bind("<Escape>", lambda e: self.destroy())  # Escapeキーで終了
        self.bind("<s>", lambda e: self.show_smile_detection_frame())  # 's'キーでSmileDetectionFrameに切り替え
        self.bind("<p>", lambda e: self.show_photo_frame())  # 'p'キーでPhotoFrameに戻す

    def show_photo_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = PhotoFrame(self, self.photo_directory, self.interval)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        logging.debug("PhotoFrameを表示しました。")

    def show_smile_detection_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = SmileDetectionFrame(self)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        logging.debug("SmileDetectionFrameを表示しました。")

def main():
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
        return

    # スライドショーの設定を取得
    try:
        photo_directory = config['slideshow']['photos_directory']
        interval = config['slideshow']['interval']
        logging.debug(f"フォトディレクトリ: {photo_directory}")
        logging.debug(f"スライドショーの間隔: {interval} ミリ秒")
    except KeyError as e:
        logging.error(f"設定ファイルに必要なキーが不足しています: {e}")
        return

    # 画面サイズを取得（必要に応じて使用）
    get_screen_sizes()

    # メインアプリケーションを初期化して実行
    try:
        app = App(photo_directory, interval)
        app.mainloop()
    except Exception as e:
        logging.error(f"アプリケーションの実行中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()
