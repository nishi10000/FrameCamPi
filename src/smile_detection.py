import cv2
import time
import logging
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from utils import load_config, setup_logging, get_timestamp
from photo_capture import CameraHandler

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
        self.font_path = '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'  # 適切なフォントパスに変更
        self.font_size = 48  # フォントサイズを調整

        # フォントファイルの存在確認
        if not os.path.exists(self.font_path):
            raise IOError(f"指定されたフォントパスが存在しません: {self.font_path}")

        print("SmileDetectionCameraHandler の初期化が完了しました。")


    def detect_smile(self, gray_frame, face_region):
        """顔領域内で笑顔を検出します"""
        x, y, w, h = face_region
        roi_gray = gray_frame[y:y+h, x:x+w]
        smiles = self.smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
        return len(smiles) > 0

    def show_preview_with_overlay(self, window_name, frame, overlay_text=None):
        """プレビューを表示し、必要に応じてオーバーレイテキストを追加（日本語対応）"""
        if overlay_text:
            # OpenCVの画像をPillowの画像に変換
            frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(frame_pil)
            font = ImageFont.truetype(self.font_path, self.font_size)
            # テキストを描画
            draw.text((50, 50), overlay_text, font=font, fill=(255, 0, 0))
            # Pillowの画像をOpenCVの画像に戻す
            frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)
        cv2.imshow(window_name, frame)

    def capture_image_on_smile(self):
        """笑顔が検出されたらカウントダウンして写真を撮影します"""
        if not self.initialize_camera():
            return

        window_name = 'Camera Preview - Smile Detection'
        self.setup_window(window_name)

        logging.info("笑顔を検出中...")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                logging.error("フレームを取得できませんでした。")
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray_frame, 1.3, 5)

            smile_detected = False

            for face in faces:
                x, y, w, h = face
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                if self.detect_smile(gray_frame, face):
                    smile_detected = True
                    logging.info("笑顔が検出されました。カウントダウンを開始します。")
                    break  # 笑顔を検出したらループを抜ける

            if smile_detected:
                self.countdown_and_capture(window_name)
                # 写真を撮影した後も続ける場合は、以下の行をコメントアウトします
                return  # 1枚の写真を撮ったら終了

            self.show_preview_with_overlay(window_name, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("ユーザーによってキャプチャが中断されました。")
                break

        self.cleanup(window_name)

    def countdown_and_capture(self, window_name):
        """カウントダウンを表示し、写真を撮影"""
        start_time = time.time()
        end_time = start_time + self.countdown_time

        while time.time() < end_time:
            ret, frame = self.cap.read()
            if not ret:
                logging.error("フレームを取得できませんでした。")
                break

            seconds_left = int(end_time - time.time()) + 1  # 残り秒数

            overlay_text = f"{seconds_left}秒後に撮影します..."
            self.show_preview_with_overlay(window_name, frame, overlay_text)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("ユーザーによってカウントダウンが中断されました。")
                return

        # 写真を撮影
        timestamp = get_timestamp()
        filename = f"{timestamp}.jpg"
        save_path = os.path.join(self.photo_directory, filename)
        self.captured_frame = self.capture_image(save_path)

        # 撮影された画像のプレビュー表示
        if self.captured_frame is not None:
            self.preview_image(self.captured_frame)

    def setup_window(self, window_name):
        """ウィンドウを設定"""
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, self.screen_width, self.screen_height)

    def cleanup(self, window_name):
        """カメラとウィンドウのリソースを解放"""
        self.cap.release()
        cv2.destroyAllWindows()
        logging.info(f"{window_name} のウィンドウが閉じられました。")

def main():
    # スクリプトのディレクトリを取得
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # ロギングの設定を初期化
    setup_logging(script_dir, log_file='debug.log')

    # config.yaml のパスを構築
    config_path = os.path.join(script_dir, 'config.yaml')

    if not os.path.exists(config_path):
        logging.error(f"設定ファイルが見つかりません: {config_path}")
        sys.exit(1)

    # 設定ファイルをロード
    try:
        config = load_config(config_filename=config_path, env_filename='.env')
    except Exception as e:
        logging.error(f"設定ファイルの読み込みに失敗しました: {e}")
        sys.exit(1)

    # 写真保存ディレクトリを取得
    photo_directory = config.get('slideshow', {}).get('photos_directory', 'photos')
    photo_directory = os.path.join(script_dir, photo_directory)

    # ディレクトリが存在しない場合は作成
    os.makedirs(photo_directory, exist_ok=True)
    logging.info(f"写真保存ディレクトリ: {photo_directory}")

    # カメラハンドラーのインスタンスを作成
    camera_config = config.get('camera', {})
    camera_handler = SmileDetectionCameraHandler(
        camera_index=camera_config.get('index', 0),
        countdown_time=camera_config.get('countdown_time', 3),
        preview_time=camera_config.get('preview_time', 3),
        photo_directory=photo_directory
    )

    # 笑顔が検出されたら画像をキャプチャして保存
    camera_handler.capture_image_on_smile()

if __name__ == "__main__":
    main()
