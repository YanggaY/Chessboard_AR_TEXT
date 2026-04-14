# Chessboard AR Text
체스보드를 인식하여 AR 텍스트를 체스보드위에 띄우는 간단한 OpenCV 프로그램입니다.

## 미리 설치 되어 있어야 하는 것들
NumPy, openCV, Python


pip install opencv-python numpy


## Default 셋업
체스보드 영상 = chessboard.mp4 <br>
체스보드 실제 칸 너비 = 25mm <br>
코너 수 (10,7) <br>
텍스트 = "GOODDAY" 

## 예시
https://github.com/YanggaY/Chessboard_AR_TEXT/issues/1#issue-4262386960

## 원하는 텍스트 띄우려면
- 체스보드가 보이는 영상을 촬영합니다
  (영상 내내 체스보드의 전체 모습이 보여야하고, 모션블러가 자제되는 충분히 밝은 곳에서 촬영하시는것을 추천드립니다.)

- 설정값 수정


  video_file = 체스보드 영상파일이름<br>
  board_pattern = 체스보드 코너 수(가로, 세로) <br>
  board_cellsize = 실제 체스보드 칸 너비(직접 자로 측정)<br>
  AR_TEXT = 띄울 텍스트<br>
  text_cx = 텍스트 가로 중심 위치<br>
  text_cy = 텍스트 세로 중심 위치
  
## 기능
- 체스보드로 카메라 캘리브레이션
- 체스보드위에 AR 텍스트 오버레이
- 한 글자씩 타이핑 되는 효과
- 텍스트 깜박이는 효과
- 시인성을 위한 텍스트 그림자 처리
- 결과 영상 저장

### 참고 
  컴퓨터 사양에 따라서 프리뷰영상의 재생이 버벅거릴 수 있으며,
  정상적으로 프로그램이 종료된 이후 출력된 output.mp4 파일을 통해 결과물을 제대로 확인할 수 있습니다.




