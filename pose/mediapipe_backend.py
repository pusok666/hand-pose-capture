import time
import cv2
import mediapipe as mp
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
model_path = (
        project_root
        / "models"
        / "hand_landmarker.task"
)
print("模型路径：", model_path)
print("模型存在：", model_path.exists())
print("模型大小：", model_path.stat().st_size / 1024 / 1024, "MB")
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
model_path = (
        project_root
        / "models"
        / "hand_landmarker.task"
)
print("模型路径：", model_path)
print("模型存在：", model_path.exists())
print("模型大小：", model_path.stat().st_size / 1024 / 1024, "MB")
class MediaPipeHandBackend:
    def __init__(self):
        # 找到 pose_capture 项目根目录
        project_root = Path(__file__).resolve().parent.parent
        # 拼出模型的绝对路径
        model_path = (
            project_root
            / "models"
            / "hand_landmarker.task"
        )
        print("模型路径：", model_path)
        print("模型存在：", model_path.exists())
        if not model_path.exists():
            raise FileNotFoundError(
                f"模型文件不存在：{model_path}"
            )
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        RunningMode = mp.tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=str(model_path)
            ),
            running_mode=RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.landmarker = HandLandmarker.create_from_options(
            options
        )
        self.last_timestamp_ms = 0
    def detect(self, frame):
        # OpenCV 是 BGR
        # MediaPipe 要 RGB
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )
        # numpy 图片 → MediaPipe Image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )
        # VIDEO 模式要求时间戳不断递增
        timestamp_ms = int(
            time.monotonic() * 1000
        )
        if timestamp_ms <= self.last_timestamp_ms:
            timestamp_ms = self.last_timestamp_ms + 1
        self.last_timestamp_ms = timestamp_ms
        # 手部检测
        result = self.landmarker.detect_for_video(
            mp_image,
            timestamp_ms
        )
        height, width = frame.shape[:2]
        hands = []
        # 一只手 = 21 个点
        for hand_index, landmarks in enumerate(
            result.hand_landmarks
        ):
            points = []
            for point_id, landmark in enumerate(landmarks):
                points.append({
                    "id": point_id,
                    # 屏幕像素坐标
                    "x": int(landmark.x * width),
                    "y": int(landmark.y * height),
                    # 深度
                    "z": float(landmark.z),
                    # 归一化坐标
                    "x_norm": float(landmark.x),
                    "y_norm": float(landmark.y)
                })
            # 左手 / 右手
            handedness = None
            handedness_score = None
            if hand_index < len(result.handedness):
                category = result.handedness[hand_index][0]
                handedness = category.category_name
                handedness_score = float(category.score)
            hands.append({
                "points": points,
                "handedness": handedness,
                "handedness_score": handedness_score
            })
        return hands
    def close(self):
        self.landmarker.close()