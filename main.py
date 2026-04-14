import cv2 as cv
import numpy as np


# 카메라 캘리브레이션 함수
def calib_camera_from_chessboard(images, board_pattern, board_cellsize):
    img_points = []
    gray = None
    for img in images:
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        ret, pts = cv.findChessboardCorners(gray, board_pattern)
        if ret == True:
            img_points.append(pts)
    assert len(img_points) > 0
    obj_pts = []                                    #3D 좌표 저장 리스트
    for r in range(board_pattern[1]):
        for c in range(board_pattern[0]):
            obj_pts.append([c, r, 0])               #z=0 고정
    obj_points = [np.array(obj_pts, dtype=np.float32) * board_cellsize] * len(img_points) 
    return cv.calibrateCamera(obj_points, img_points, gray.shape[::-1], None, None) 


# 텍스트 이미지 생성 함수
def make_text_image(text, width=512, height=128, font_scale=3.0):
    img = np.zeros((height, width, 4), dtype=np.uint8)      #투명 배경 이미지 생성
    font = cv.FONT_HERSHEY_DUPLEX                           #폰트 설정
    thickness = 4                                           #텍스트 두께
    text_size, _ = cv.getTextSize(text, font, font_scale, thickness)
    tx = (width - text_size[0]) // 2
    ty = (height + text_size[1]) // 2
    cv.putText(img, text, (tx+3, ty+3), font, font_scale, (100, 100, 100, 255), thickness + 8) #텍스트 그림자표현
    cv.putText(img, text, (tx, ty),     font, font_scale, (0, 255, 255, 255),   thickness)     #텍스트
    mask = np.all(img[:, :, :3] == [0, 0, 0], axis=2)
    img[~mask, 3] = 255
    img[mask, 3] = 0
    return img


#AR 렌더링 함수
def draw_text_ar(frame, text_img, cx, cy, cellsize, rvec, tvec, K, dist_coeff, alpha_value=255):
    h_px, w_px = text_img.shape[:2]                             #텍스트 이미지 가로/세로 픽셀 크기
    aspect = w_px / h_px                                        #가로세로 비율
    sign_h = cellsize * 2.0                                     #텍스트 공간 높이 
    sign_w = sign_h * aspect                                    #텍스트 공간 너비
    half_w = sign_w / 2.0                                       #텍스트 공간 너비 절반
    model_pts = np.float32([
        [cx - half_w, cy, -sign_h],
        [cx - half_w, cy, 0],
        [cx + half_w, cy, -sign_h],
        [cx + half_w, cy, 0],
    ])
    img_pts, _ = cv.projectPoints(model_pts, rvec, tvec, K, dist_coeff)
    dst_pts = img_pts.reshape(-1, 2).astype(np.float32)
    src_pts = np.float32([
        [0, 0],
        [0, h_px],
        [w_px, 0],
        [w_px, h_px],
    ])
    M = cv.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv.warpPerspective(text_img, M, (frame.shape[1], frame.shape[0]),
                                borderMode=cv.BORDER_CONSTANT, borderValue=(0,0,0,0))
    alpha_ch = warped[:, :, 3]
    _, mask = cv.threshold(alpha_ch, 1, 255, cv.THRESH_BINARY)
    overlay_bgr = warped[:, :, :3].astype(np.uint8)
    alpha_ratio = alpha_value / 255.0
    blended = cv.addWeighted(overlay_bgr, alpha_ratio, frame, 1 - alpha_ratio, 0)
    cv.copyTo(src=blended, dst=frame, mask=mask)

#기본 설정
video_file     = "chessboard.mp4"                   #입력 영상
board_pattern  = (10, 7)                            #체스보드 코너 수
board_cellsize = 25.0                               #실제 체스보드 칸 너비
AR_TEXT        = "GOODDAY"                          #띄울 텍스트
text_cx        = 4.5 * board_cellsize               #텍스트 가로 중심 위치
text_cy        = 3.0 * board_cellsize               #텍스트 세로 중심 위치


# 영상 열기 및 저장파일 설정
cap = cv.VideoCapture(video_file)
assert cap.isOpened()
frame_width  = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
fps          = cap.get(cv.CAP_PROP_FPS)
#저장 파일 옵션
out = cv.VideoWriter('output.mp4', cv.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))


#캘리브레이션 샘플 추출 및 실행
chessboard_frames = []
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    found, _ = cv.findChessboardCorners(gray, board_pattern, cv.CALIB_CB_FAST_CHECK)
    if found:
        chessboard_frames.append(frame)
    if len(chessboard_frames) >= 20:
        break

assert len(chessboard_frames) > 0
ret, K, dist_coeff, _, _ = calib_camera_from_chessboard(chessboard_frames, board_pattern, board_cellsize)


#3D 좌표 설정
obj_pts = []
for r in range(board_pattern[1]):
    for c in range(board_pattern[0]):
        obj_pts.append([c, r, 0])

objp = np.array(obj_pts, dtype=np.float32) * board_cellsize

cap.set(cv.CAP_PROP_POS_FRAMES, 0)
rvec, tvec      = None, None
alpha_value     = 0
alpha_direction = 1
frame_count     = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)                #흑백 변환
    found, corners = cv.findChessboardCorners(gray, board_pattern, cv.CALIB_CB_FAST_CHECK)  #체스보드코너찾기
    if found:
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)        #코너 정밀화 기준
        corners  = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)         #코너 위치 정밀화하기
        _, rvec, tvec = cv.solvePnP(objp, corners, K, dist_coeff)                       #rvec, tvec 계산
    if rvec is not None:
        char_count   = min(frame_count // 10, len(AR_TEXT))           #10프레임마다 글자 하나씩 추가
        current_text = AR_TEXT[:char_count]
        if current_text:
            text_img = make_text_image(current_text)                  #텍스트 이미지 생성
            alpha_value += alpha_direction * 10                       #투명도 증감
            if alpha_value >= 255 or alpha_value <= 0:                #글자 깜박이게 하기위해 최대 최소에 도달 하면 
                alpha_direction *= -1                                 #알파 증감 방향 반전
            alpha_value = np.clip(alpha_value, 0, 255)                #범위 안 벗어나게
            draw_text_ar(frame, text_img, text_cx, text_cy, board_cellsize,
                         rvec, tvec, K, dist_coeff, alpha_value)
    frame_count += 1
    out.write(frame)
    cv.imshow('AR Text', frame)
    if cv.waitKey(1) == 27:                                           #ESC 누르면 강제종료
        break

cap.release()
out.release()
cv.destroyAllWindows()
print("output.mp4 저장 완료")