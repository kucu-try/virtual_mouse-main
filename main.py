import cv2
import time
import numpy as np
import hand_detector as hd  # 손을 감지하는데 사용할 사용자 정의 모듈
import pyautogui  # 마우스 제어에 사용되는 모듈

# 카메라의 너비와 높이 설정
wCam, hCam = 1080, 800

# 프레임 크기 및 부드럽게 하기 위한 값 설정
frameR = 100
smoothening = 7

# 이전 시간 및 이전 및 현재 좌표 초기화
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

# 카메라 열기
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

# 손 감지 객체 생성
detector = hd.handDetector(detectionCon=0.7)

# 화면 크기 가져오기
wScr, hScr = pyautogui.size()
print(wScr, hScr)

while True:
    # 카메라로부터 이미지 읽기
    success, img = cap.read()

    # 손 감지 함수를 사용하여 이미지에서 손 감지
    img = detector.findHands(img)

    # 손 위치 찾기
    lmList, bbox = detector.findPosition(img)
    
    # 출력 이미지 복사
    output = img.copy()

    if len(lmList) != 0:
        # 손가락 리스트에서 인덱스와 가운데 손가락의 상태 가져오기
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        fingers = detector.fingersUp()

        # 화면에 사각형 그리기
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (205, 250, 255), -1)
        img = cv2.addWeighted(img, 0.5, output, 1 - .5, 0, output)

        # 인덱스 손가락만 올려져 있을 때 : 이동 모드
        if fingers[1] == 1 and fingers[2] == 0:
            # 좌표 변환
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            # 값 부드럽게 하기
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # 마우스 이동
            pyautogui.moveTo(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 6, (255, 28, 0), cv2.FILLED)
            plocX, plocY = clocX, clocY

        # 인덱스와 가운데 손가락이 모두 올려져 있을 때 : 클릭 모드
        if fingers[1] == 1 and fingers[2] == 1:
            # 손가락 사이의 거리 찾기
            length, img, lineInfo = detector.findDistance(8, 12, img)

            # 거리가 짧으면 클릭
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 6, (0, 255, 0), cv2.FILLED)
                pyautogui.click()

    # 현재 시간 및 FPS 계산
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    # 화면에 이미지 출력
    cv2.imshow("Vitual mouse monitor", cv2.flip(img, 1))
    cv2.setWindowProperty("Vitual mouse monitor", cv2.WND_PROP_TOPMOST, 1)
    cv2.waitKey(1)