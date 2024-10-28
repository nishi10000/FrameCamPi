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

def put_japanese_text(img, text, position, font, color=(0, 255, 0)):
    """
    Pillowを使用して画像に日本語テキストを描画し、OpenCV形式に変換します。

    :param img: OpenCV形式の画像（BGR）
    :param text: 描画するテキスト（日本語可）
    :param position: テキストの位置（x, y）
    :param font: PIL.ImageFont インスタンス
    :param color: テキストの色（BGR）
    :return: テキストが描画されたOpenCV形式の画像
    """
    import numpy as np
    from PIL import Image, ImageDraw

    # OpenCVの画像をRGBに変換
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(pil_img)

    # テキストの描画
    draw.text(position, text, font=font, fill=color[::-1])  # PillowはRGB、OpenCVはBGRなので色を反転

    # Pillow画像をOpenCV形式に変換
    img_with_text = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return img_with_text

class SmileDetectionCameraHandler(CameraHandler):
    def __init__(self, camera_index=0, countdown_time=3, preview_time=3, photo_directory='photos'):
        super().__init__(camera_index, countdown_time, preview_time, photo_directory)

        # Haar Cascade ディレクトリの取得
        self.haarcascades_path = self.get_haarcascades_path()

        # カスケードのロード
        self.face_cascade = self.load_cascade('haarcascade_frontalface_default.xml')
        self.smile_cascade = self.load_cascade('haarcascade_smile.xml')

        # フォントのロード
        self.font_path = self.get_font_path()
        self.font_size = 48  # フォントサイズを調整
        self.font = self.load_font(self.font_path, self.font_size)

        logging.info("SmileDetectionCameraHandler の初期化が完了しました。")

    def get_haarcascades_path(self):
        """
        Haar Cascade のパスを取得します。
        """
        try:
            haarcascades = cv2.data.haarcascades
            logging.debug(f"cv2.data.haarcascades のパスを使用: {haarcascades}")
            return haarcascades
        except AttributeError:
            fallback_path = '/usr/share/opencv4/haarcascades/'
            logging.warning(f"cv2.data.haarcascades が存在しません。フォールバックパスを使用します: {fallback_path}")
            return fallback_path

    def load_cascade(self, filename):
        """
        カスケードファイルをロードします。
        """
        cascade_path = os.path.join(self.haarcascades_path, filename)
        if not os.path.exists(cascade_path):
            logging.error(f"カスケードファイルが見つかりません: {cascade_path}")
            raise IOError(f"カスケードファイルをロードできません: {cascade_path}")
        cascade = cv2.CascadeClassifier(cascade_path)
        if cascade.empty():
            logging.error(f"カスケードの読み込みに失敗しました: {cascade_path}")
            raise IOError(f"カスケードの読み込みに失敗しました: {cascade_path}")
        logging.info(f"カスケードをロードしました: {cascade_path}")
        return cascade

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

    def load_font(self, font_path, font_size):
        """
        フォントをロードします。
        """
        if not os.path.exists(font_path):
            logging.warning(f"指定されたフォントパスが存在しません: {font_path}. デフォルトフォントを使用します。")
            return ImageFont.load_default()
        try:
            return ImageFont.truetype(font_path, font_size)
        except Exception as e:
            logging.error(f"フォントのロードに失敗しました: {e}")
            return ImageFont.load_default()


class SmileDetectionFrame(tk.Frame):
    def __init__(self, parent, camera_handler: SmileDetectionCameraHandler, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.camera_handler = camera_handler

        # カメラの初期化
        if not self.camera_handler.initialize_camera():
            logging.error("カメラの初期化に失敗しました。アプリケーションを終了します。")
            parent.destroy()
            return

        # カスケードの設定
        self.face_cascade = self.camera_handler.face_cascade
        self.smile_cascade = self.camera_handler.smile_cascade

        # フォント設定
        self.font = self.camera_handler.font

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
        self.stop_preview = False

        # プレビュー更新開始
        self.after(0, self.update_frame)

    def on_resize(self, event):
        """ウィンドウのサイズ変更に対応"""
        self.frame_width = event.width
        self.frame_height = event.height

    def update_frame(self):
        if getattr(self, 'stop_preview', False):
            return

        try:
            ret, frame = self.camera_handler.cap.read()
            if not ret:
                logging.error("フレームを取得できませんでした。")
                self.after(100, self.update_frame)  # 少し待って再試行
                return

            if not self.is_capturing:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray_frame, 1.3, 5)

                smile_detected = False

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    roi_gray = gray_frame[y:y + h, x:x + w]
                    smiles = self.smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
                    if len(smiles) > 0:
                        smile_detected = True
                        text_position = (x, y - 10)
                        text = "笑顔を検出!"
                        frame = put_japanese_text(frame, text, text_position, self.font, color=(0, 255, 0))
                        break  # 笑顔を検出したらループを抜ける

                if smile_detected:
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

        except Exception as e:
            logging.error(f"フレームの更新中にエラーが発生しました: {e}")

        # 次のフレーム更新をスケジュール
        self.after(30, self.update_frame)  # 約33fps

    def capture_image(self):
        try:
            ret, frame = self.camera_handler.cap.read()
            if ret:
                timestamp = get_timestamp()
                filename = f"{timestamp}.jpg"
                save_path = os.path.join(self.camera_handler.photo_directory, filename)
                cv2.imwrite(save_path, frame)
                logging.info(f"画像が保存されました: {save_path}")

                # 撮影された画像のプレビュー表示（オプション）
                self.preview_captured_image(frame)

                # インターバル中のメッセージを表示
                self.status_label.config(text="撮影完了！3秒間お待ちください。")

            else:
                logging.error("画像のキャプチャに失敗しました。")
                self.after(2000, lambda: self.status_label.config(text="笑顔を検出しています..."))
        except Exception as e:
            logging.error(f"画像のキャプチャ中にエラーが発生しました: {e}")
            self.after(2000, lambda: self.status_label.config(text="笑顔を検出しています..."))
        finally:
            # 3秒後に笑顔検出を再開
            self.after(3000, self.resume_detection)

    def resume_detection(self):
        """笑顔検出を再開します"""
        self.is_capturing = False
        self.status_label.config(text="笑顔を検出しています...")

    def preview_captured_image(self, frame):
        """撮影された画像を一時的に表示します"""
        try:
            window = tk.Toplevel(self)
            window.title("撮影画像プレビュー")

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
        except Exception as e:
            logging.error(f"プレビュー表示中にエラーが発生しました: {e}")

    def destroy(self):
        self.stop_preview = True
        self.camera_handler.release_camera()
        logging.info("カメラをリリースしました。")
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
    try:
        config = load_config(config_path)
    except Exception as e:
        logging.error(f"設定ファイルの読み込みに失敗しました: {e}")
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
    root.title("笑顔検出アプリ")

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
