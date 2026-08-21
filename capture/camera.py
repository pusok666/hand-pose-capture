import cv2
class Camera:
    def __init__(self, camera_id=0, width=1280, height=720):
        # 打开摄像头
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            raise RuntimeError("摄像头打开失败")
        # 请求摄像头使用指定分辨率
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    def read(self):
        # 从摄像头读取一帧
        ok, frame = self.cap.read()
        if not ok:
            raise RuntimeError("读取摄像头画面失败")

        return frame

    def get_resolution(self):
        # 获取摄像头实际使用的分辨率
        width = int(
            self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        )

        height = int(
            self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )

        return width, height

    def release(self):
        # 释放摄像头
        self.cap.release()