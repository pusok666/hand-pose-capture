import cv2

class Camera:
    def __init__(self, camera_id=0, width=1280, height=720):
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            raise RuntimeError("摄像头打开失败")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            raise RuntimeError("读取摄像头画面失败")
        return frame
    def release(self):
        self.cap.release()