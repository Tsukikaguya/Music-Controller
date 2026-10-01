import cv2

# 開啟攝影機
cap = cv2.VideoCapture(0)

# 檢查攝影機
if not cap.isOpened():
    print("Camera cannot open")
    exit()


while True:

    # 讀取影像
    ret, frame = cap.read()

    if not ret:
        print("Cannot receive frame")
        break


    # 鏡像
    frame = cv2.flip(frame, 1)


    # 顯示畫面
    cv2.imshow(
        "Camera Test",
        frame
    )


    # 取得鍵盤輸入
    key = cv2.waitKey(10) & 0xff


    # 按 q 或按右上角 X 離開
    if key == ord('q') or cv2.getWindowProperty(
        "Camera Test",
        cv2.WND_PROP_VISIBLE
    ) < 1:
        break



# 關閉
cap.release()
cv2.destroyAllWindows()

print("Camera released")