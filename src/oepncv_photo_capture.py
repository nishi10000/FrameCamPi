import cv2

# カメラデバイスの初期化
cap = cv2.VideoCapture(0)

# 画像を取得
ret, frame = cap.read()

# 画像が正しく取得できたか確認
if ret:
    # 画像をファイルに保存
    cv2.imwrite('captured_image.jpg', frame)
    print("Image saved as captured_image.jpg")
else:
    print("Failed to capture image")

# カメラデバイスの解放
cap.release()
cv2.destroyAllWindows()