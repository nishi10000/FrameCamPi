# smile_detection.py

import cv2
import time
import logging
import os
import sys
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageFont, ImageTk
from utils import load_config, setup_logging, get_timestamp
from photo_capture import CameraHandler  # CameraHandler をインポート


class SmileDetectionCameraHandler(CameraHandler):
    def __init__(self, camera_index=0, countdown_time=3, preview_time=3, photo_directory='photos'):
        super().__init__(camera_index, countdown_time, preview_time, photo_directory)
        
        # デフォルトのHaar Cascadeディレクトリ
        fallback_haarcascade_dir = '/usr/share/opencv4/haarcascades/'
        fallback_face_cascade_path = os.path.join(fallback_haarcascade_dir, 'haarcascade_frontalface_default.xml')
        fallback_smile_cascade_path = os.path.join(fallback_haarcascade_dir, 'haarcascade_smile.xml')
        
        # 初期化フラグ
        loaded_via_cv_data = False
        
        try:
            # cv2.data.haarcascadesが存在するか確認
            haarcascades = cv2.data.haarcascades
            print(f"Using cv2.data.haarcascades path: {haarcascades}")
            loaded_via_cv_data = True
        except AttributeError:
            print("cv2.data.haarcascades が存在しません。フォールバックパスを使用します。")
            haarcascades = fallback_haarcascade_dir
        
        # 顔検出カスケードのロード
        face_cascade_path = os.path.join(haarcascades, 'haarcascade_frontalface_default.xml')
        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        if self.face_cascade.empty():
            if loaded_via_cv_data:
                print(f"{face_cascade_path} の読み込みに失敗しました。フォールバックパスを使用します。")
                self.face_cascade = cv2.CascadeClassifier(fallback_face_cascade_path)
                if self.face_cascade.empty():
                    raise IOError(f"顔検出カスケードを {face_cascade_path} および {fallback_face_cascade_path} から読み込めません。")
            else:
                raise IOError(f"顔検出カスケードを {face_cascade_path} から読み込めません。")
        else:
            print(f"顔検出カスケードを {face_cascade_path} からロードしました。")
        
        # 笑顔検出カスケードのロード
        smile_cascade_path = os.path.join(haarcascades, 'haarcascade_smile.xml')
        self.smile_cascade = cv2.CascadeClassifier(smile_cascade_path)
        if self.smile_cascade.empty():
            if loaded_via_cv_data:
                print(f"{smile_cascade_path} の読み込みに失敗しました。フォールバックパスを使用します。")
                self.smile_cascade = cv2.CascadeClassifier(fallback_smile_cascade_path)
                if self.smile_cascade.empty():
                    raise IOError(f"笑顔検出カスケードを {smile_cascade_path} および {fallback_smile_cascade_path} から読み込めません。")
            else:
                raise IOError(f"笑顔検出カスケードを {smile_cascade_path} から読み込めません。")
        else:
            print(f"笑顔検出カスケードを {smile_cascade_path} からロードしました。")
        
        # 日本語フォントのパスを指定
        self.font_path = self.get_font_path()
        self.font_size = 48  # フォントサイズを調整

        # フォントファイルの存在確認
        if not os.path.exists(self.font_path):
            logging.warning(f"指定されたフォントパスが存在しません: {self.font_path}. デフォルトフォントを使用します。")
            self.font = ImageFont.load_default()
        else:
            self.font = ImageFont.truetype(self.font_path, self.font_size)

        print("SmileDetectionCameraHandler の初期化が完了しました。")

    def get_font_path(self):
        """
        システムに応じた日本語フォントのパスを返します。
        必要に応じてパスを変更してください。
        """
        if sys.platform.startswith('linux'):
            # Linux の場合
            return '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'  # 適切なフォントパスに変更
        elif sys.platform == 'darwin':
            # macOS の場合
            return '/Library/Fonts/Arial Unicode.ttf'  # 適切なフォントパスに変更
        elif sys.platform == 'win32':
            # Windows の場合
            return 'C:/Windows/Fonts/msgothic.ttc'  # 適切なフォントパスに変更
        else:
            raise IOError("対応していないOSです。フォントパスを手動で設定してください。")


class SmileDetectionFrame(tk.Frame):
    def __init__(self, parent, camera_handler: SmileDetectionCameraHandler, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.camera_handler = camera_handler
        self.camera_handler.initialize_camera()

        # 顔と笑顔の検出用カスケードファイルのパスを設定
        self.face_cascade = self.camera_handler.face_cascade
        self.smile_cascade = self.camera_handler.smile_cascade

        # フォント設定
        self.font_path = self.camera_handler.font_path
        self.font_size = self.camera_handler.font_size
        try:
            self.font = ImageFont.truetype(self.font_path, self.font_size)
        except IOError:
            logging.error(f"フォントファイルが見つかりません: {self.font_path}")
            self.font = ImageFont.load_default()

        # 画像表示用ラベル
        self.image_label = ttk.Label(self)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # ステータス表示ラベル
        self.status_label = ttk.Label(self, text="笑顔を検出しています...", font=("Arial", 16))
        self.status_label.pack(side=tk.BOTTOM, pady=10)

        # フレームのリサイズに対応するためのバインド
        self.bind("<Configure>", self.on_resize)

        # フレームのサイズを保持
        self.frame_width = self.winfo_width()
        self.frame_height = self.winfo_height()

        # フラグ: 現在キャプチャ中かどうか
        self.is_capturing = False

        # プレビュー更新開始
        self.after(0, self.update_frame)

    def on_resize(self, event):
        """ウィンドウのサイズ変更に対応"""
        self.frame_width = event.width
        self.frame_height = event.height

    def update_frame(self):
        if getattr(self, 'stop_preview', False):
            return

        ret, frame = self.camera_handler.cap.read()
        if not ret:
            logging.error("フレームを取得できませんでした。")
            self.after(100, self.update_frame)  # 少し待って再試行
            return

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_frame, 1.3, 5)

        smile_detected = False

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray_frame[y:y+h, x:x+w]
            smiles = self.smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
            if len(smiles) > 0:
                smile_detected = True
                cv2.putText(frame, "Smile Detected!", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                break  # 笑顔を検出したらループを抜ける

        if smile_detected and not self.is_capturing:
            self.is_capturing = True
            self.status_label.config(text="笑顔が検出されました！写真を撮影します。")
            # メッセージ表示後に写真撮影を開始（1秒後）
            self.after(1000, self.capture_image)

        # OpenCV の BGR から RGB に変換
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)

        # フレームのサイズに合わせて画像をリサイズ
        img = img.resize((self.frame_width, self.frame_height), Image.ANTIALIAS)

        # Pillow を使用して画像を Tkinter 用に変換
        imgtk = ImageTk.PhotoImage(image=img)
        self.image_label.imgtk = imgtk  # 参照を保持
        self.image_label.configure(image=imgtk)

        # 次のフレーム更新をスケジュール
        self.after(30, self.update_frame)  # 約33fps

    def capture_image(self):
        ret, frame = self.camera_handler.cap.read()
        if ret:
            timestamp = get_timestamp()
            filename = f"{timestamp}.jpg"
            save_path = os.path.join(self.camera_handler.photo_directory, filename)
            cv2.imwrite(save_path, frame)
            logging.info(f"画像が保存されました: {save_path}")

            # 撮影された画像のプレビュー表示（オプション）
            self.preview_captured_image(frame)

            # メッセージを2秒後にリセット
            self.after(2000, lambda: self.status_label.config(text="笑顔を検出しています..."))
        else:
            logging.error("画像のキャプチャに失敗しました。")
            # メッセージをリセット
            self.after(2000, lambda: self.status_label.config(text="笑顔を検出しています..."))

        self.is_capturing = False  # キャプチャ完了

    def preview_captured_image(self, frame):
        """撮影された画像を一時的に表示します"""
        window = tk.Toplevel(self)
        window.title("Captured Image")

        # OpenCV の BGR から RGB に変換
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img = img.resize((400, 300), Image.ANTIALIAS)  # プレビュー用にリサイズ
        imgtk = ImageTk.PhotoImage(image=img)

        label = ttk.Label(window, image=imgtk)
        label.image = imgtk  # 参照を保持
        label.pack()

        # 一定時間後にウィンドウを閉じる
        window.after(3000, window.destroy)  # 3秒後に閉じる

    def destroy(self):
        self.stop_preview = True
        self.camera_handler.cap.release()
        super().destroy()


def main():
    # スクリプトのディレクトリを取得
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # ログ設定を初期化
    setup_logging(script_dir, log_file='smile_detection.log')
    logging.debug("ログ設定を初期化しました。")

    # config.yaml のパスを指定
    config_path = os.path.join(script_dir, 'config.yaml')

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
    photo_directory = os.path.join(script_dir, photo_directory)

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

    # フルスクリーン設定（必要に応じて変更）
    root.attributes('-fullscreen', True)
    logging.debug("ウィンドウをフルスクリーンに設定しました。")

    # SmileDetectionFrame を作成してパック
    smile_detection_frame = SmileDetectionFrame(root, camera_handler)
    smile_detection_frame.pack(fill=tk.BOTH, expand=True)

    # キーボードイベントのバインド
    root.bind("<Escape>", lambda e: root.destroy())  # Escapeキーで終了

    # Tkinter のメインループを開始
    try:
        root.mainloop()
    except Exception as e:
        logging.error(f"アプリケーションの実行中にエラーが発生しました: {e}")
    finally:
        # リソースのクリーンアップ
        smile_detection_frame.destroy()
        logging.info("アプリケーションを終了しました。")


if __name__ == "__main__":
    main()
