import cv2
import time
import threading
from utils import get_screen_sizes  # utils.pyからインポート

def countdown_timer(countdown_time, countdown_event):
    """
    カウントダウンを非同期で行い、終了時にイベントを設定します。

    Parameters:
    countdown_time (int): カウントダウンの秒数
    countdown_event (threading.Event): カウントダウン終了を知らせるイベント
    """
    for i in range(countdown_time, 0, -1):
        print(f"Countdown: {i}")
        time.sleep(1)  # カウントダウンを1秒ごとに進行
    countdown_event.set()  # カウントダウンが終了したことを通知

def capture_image_with_resized_window(countdown_time=3, save_path='captured_image.jpg', preview_time=3):
    """
    非同期でカウントダウンを表示しながらカメラのプレビューを続け、カウントダウン終了後に写真を撮影し、
    撮影された画像を画面サイズに合わせてプレビュー表示します。

    Parameters:
    countdown_time (int): カウントダウンの秒数
    save_path (str): 撮影した画像の保存先
    preview_time (int): 撮影後に写真をプレビューする時間（秒）
    """
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # 画面サイズを取得
    screen_width, screen_height = get_screen_sizes()

    countdown_event = threading.Event()  # カウントダウン終了を通知するためのイベント
    countdown_thread = threading.Thread(target=countdown_timer, args=(countdown_time, countdown_event))
    countdown_thread.start()  # カウントダウンを別スレッドで開始

    captured_frame = None

    # カウントダウン中のプレビューウィンドウを設定
    cv2.namedWindow('Camera Preview - Countdown', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Camera Preview - Countdown', screen_width, screen_height)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break
        
        # カウントダウンが続いている間、カウントダウンの数字を描画
        if not countdown_event.is_set():
            remaining_time = int(countdown_time - (time.time() % countdown_time))
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, str(remaining_time), (50, 50), font, 2, (255, 0, 0), 3, cv2.LINE_AA)
        else:
            # カウントダウン終了後に写真を撮影し、プレビューのためにフレームを保存
            captured_frame = frame
            cv2.imwrite(save_path, captured_frame)
            print(f"Image saved as {save_path}")
            break
        
        # カウントダウン中のプレビューを表示
        cv2.imshow('Camera Preview - Countdown', frame)

        # 'q'キーを押すと手動で終了可能
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # カメラを解放
    cap.release()

    # 撮影された画像を画面サイズに合わせてプレビュー表示
    if captured_frame is not None:
        # 撮影後のウィンドウを画面サイズで作成
        cv2.namedWindow('Captured Image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Captured Image', screen_width, screen_height)

        start_time = time.time()
        while time.time() - start_time < preview_time:
            cv2.imshow('Captured Image', captured_frame)
            # 'q'キーを押すとプレビューを終了できる
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        print(f"Preview ended after {preview_time} seconds.")

    # ウィンドウを解放
    cv2.destroyAllWindows()


def initialize_camera(camera_index=0):
    """
    カメラデバイスを初期化します。

    Parameters:
    camera_index (int): 使用するカメラのインデックス (デフォルト: 0)

    Returns:
    cap: カメラデバイスのキャプチャオブジェクト
    """
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None
    return cap

def capture_image(cap, save_path='captured_image.jpg'):
    """
    カメラから画像をキャプチャし、指定したパスに保存します。

    Parameters:
    cap: カメラデバイスのキャプチャオブジェクト
    save_path (str): 保存するファイルのパス (デフォルト: 'captured_image.jpg')
    """
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(save_path, frame)
        print(f"Image saved as {save_path}")
    else:
        print("Failed to capture image")

def release_camera(cap):
    """
    カメラデバイスを解放します。

    Parameters:
    cap: カメラデバイスのキャプチャオブジェクト
    """
    cap.release()
    cv2.destroyAllWindows()

import cv2

def start_camera_preview():
    """
    カメラからのリアルタイム映像をプレビュー表示します。
    """
    cap = cv2.VideoCapture(0)  # カメラデバイスの初期化 (0はデフォルトのカメラ)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break
        
        # ウィンドウにリアルタイム映像を表示
        cv2.imshow('Camera Preview', frame)
        
        # 'q'キーを押すと終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # カメラとウィンドウを解放
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # get_screen_sizes()
    # start_camera_preview()
    capture_image_with_resized_window(3, 'captured_image.jpg')

# if __name__ == "__main__":
#     # カメラを初期化
#     cap = initialize_camera()

#     if cap:
#         # 画像をキャプチャして保存
#         capture_image(cap, 'captured_image.jpg')
        
#         # カメラを解放
#         release_camera(cap)
