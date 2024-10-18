import cv2
import time
import logging
from utils import get_screen_sizes, load_config, setup_logging, get_timestamp
from photo_capture import CameraHandler
import sys
import os

class SmileDetectionCameraHandler(CameraHandler):
    def __init__(self, camera_index=0, countdown_time=3, preview_time=3, photo_directory='photos'):
        super().__init__(camera_index, countdown_time, preview_time, photo_directory)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

    def detect_smile(self, gray_frame, face_region):
        """顔領域内で笑顔を検出します"""
        x, y, w, h = face_region
        roi_gray = gray_frame[y:y+h, x:x+w]
        smiles = self.smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
        return len(smiles) > 0

    def show_preview_with_overlay(self, window_name, frame, overlay_text=None):
        """プレビューを表示し、必要に応じてオーバーレイテキストを追加"""
        if overlay_text:
            cv2.putText(frame, overlay_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3, cv2.LINE_AA)
        cv2.imshow(window_name, frame)

    def capture_image_on_smile(self, save_path):
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

            for face in faces:
                x, y, w, h = face
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                if self.detect_smile(gray_frame, face):
                    logging.info("笑顔が検出されました。3秒後に写真を撮影します。")
                    self.countdown_and_capture(window_name, frame, save_path)
                    return  # 1枚の写真を撮ったら終了

            self.show_preview_with_overlay(window_name, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("ユーザーによってキャプチャが中断されました。")
                break

        self.cleanup(window_name)

    def countdown_and_capture(self, window_name, frame, save_path):
        """カウントダウンを表示し、写真を撮影"""
        for i in range(self.countdown_time, 0, -1):
            self.show_preview_with_overlay(window_name, frame, f"{i}秒後に撮影します...")
            time.sleep(1)

        self.captured_frame = self.capture_image(save_path)

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

    timestamp = get_timestamp()

    # 写真保存ディレクトリを取得
    photo_directory = config.get('slideshow', {}).get('photos_directory', 'photos')
    photo_directory = os.path.join(script_dir, photo_directory)

    # ディレクトリが存在しない場合は作成
    os.makedirs(photo_directory, exist_ok=True)

    # タイムスタンプ付きのファイル名を作成
    filename = f"{timestamp}.jpg"
    file_path = os.path.join(photo_directory, filename)

    # 笑顔検出付きカメラハンドラーのインスタンスを作成
    camera_config = config.get('camera', {})
    camera_handler = SmileDetectionCameraHandler(
        camera_index=camera_config.get('index', 0),
        countdown_time=camera_config.get('countdown_time', 3),
        preview_time=camera_config.get('preview_time', 3),
        photo_directory=photo_directory
    )

    # 笑顔が検出されたら画像をキャプチャして保存
    camera_handler.capture_image_on_smile(file_path)


if __name__ == "__main__":
    main()
