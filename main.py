import cv2
import time
import json
import mediapipe as mp
from pose.landmark_smoother import LandmarkSmoother
from pathlib import Path
from pose_capture.pose.hand_metrics import analyze_hand
from capture.camera import Camera
from pose.mediapipe_backend import MediaPipeHandBackend
from visualization.skeleton_drawer import draw_hand_skeleton
from storage.json_writer import KeypointWriter
print("MediaPipe version:", mp.__version__)
def main():
    # 1. 创建多个摄像头
    cameras = [
        Camera(
            camera_id=0,
            width=1280,
            height=720
        ),
        # 有第二个摄像头时再打开
        # Camera(
        #     camera_id=1,
        #     width=1280,
        #     height=720
        # ),
    ]
    # 每个摄像头对应一个 MediaPipe backend
    pose_backends = [
        MediaPipeHandBackend()
        for _ in cameras
    ]
    smoothers = [
        LandmarkSmoother(alpha=0.2)
        for _ in cameras
    ]
    # 2. 输出目录
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    # 3. 录像相关变量
    recording = False
    writers = []
    keypoint_writer = None
    frame_id = 0
    recording_start_time = None
    # 4. FPS
    last_time = time.perf_counter()
    fps = 0.0
    try:
        while True:
            # 5. 读取所有摄像头
            frames = []
            for camera in cameras:
                frame = camera.read()
                frames.append(frame)
            # 6. 检测每个摄像头里的手
            all_hands = []
            for i, frame in enumerate(frames):
                # 先检测手部关键点
                hands = pose_backends[i].detect(frame)#再做平滑
                hands = smoothers[i].smooth(hands)
                all_hands.append(hands)
            # 7. 计算 FPS
            current_time = time.perf_counter()
            delta = current_time - last_time
            if delta > 0:
                fps = 1.0 / delta
            last_time = current_time
            # 8. 正在录制时保存数据
            if recording:
                # 从本次采集开始后经过了多少毫秒
                timestamp_ms = int(
                    (
                        time.perf_counter()
                        - recording_start_time
                    )
                    * 1000
                )
                # 保存原始视频
                for writer, frame in zip(
                    writers,
                    frames
                ):
                    writer.write(frame)
                # 保存关键点
                for camera_id, hands in enumerate(
                    all_hands
                ):
                    keypoint_writer.write(
                        frame_id=frame_id,
                        timestamp_ms=timestamp_ms,
                        camera_id=camera_id,
                        hands=hands
                    )
                frame_id += 1
            # 9. 显示所有摄像头
            for i, frame in enumerate(frames):
                # 很重要：
                # 不直接往原始 frame 上画
                # 做一个副本专门用于显示
                display_frame = frame.copy()
                # 画骨骼
                display_frame = draw_hand_skeleton(
                    display_frame,
                    all_hands[i]
                )
                analysis_result = None
                if len(all_hands[i]) > 0:
                    analysis_result = analyze_hand(
                        all_hands[i][0]
                    )
                # 摄像头编号
                cv2.putText(
                    display_frame,
                    f"Camera {i}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
                # FPS
                cv2.putText(
                    display_frame,
                    f"FPS: {fps:.1f}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )
                # 检测到几只手
                cv2.putText(
                    display_frame,
                    f"Hands: {len(all_hands[i])}",
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )
                # 当前帧号
                cv2.putText(
                    display_frame,
                    f"Frame: {frame_id}",
                    (20, 160),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )
                for i, frame in enumerate(frames):
                    display_frame = frame.copy()
                    # 画骨架
                    display_frame = draw_hand_skeleton(
                        display_frame,
                        all_hands[i]
                    )
                    # ===== 手部分析 =====
                    analysis_result = None

                    if len(all_hands[i]) > 0:
                        analysis_result = analyze_hand(
                            all_hands[i][0]
                        )
                    if analysis_result is not None:
                        pip_angle = analysis_result[
                            "index_pip_angle"
                        ]
                        dip_angle = analysis_result[
                            "index_dip_angle"
                        ]
                        openness = analysis_result[
                            "hand_openness"
                        ]
                        cv2.putText(
                            display_frame,
                            f"Index PIP: {pip_angle:.1f} deg",
                            (20, 240),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 255),
                            2
                        )
                        cv2.putText(
                            display_frame,
                            f"Index DIP: {dip_angle:.1f} deg",
                            (20, 280),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 255),
                            2
                        )
                        cv2.putText(
                            display_frame,
                            f"Hand openness: {openness:.2f}",
                            (20, 320),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 255),
                            2
                        )
                    # 摄像头编号
                    cv2.putText(
                        display_frame,
                        f"Camera {i}",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )
                # 录像状态
                if recording:
                    cv2.putText(
                        display_frame,
                        "REC",
                        (20, 200),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        3
                    )
                # 显示窗口
                cv2.imshow(
                    f"Camera {i}",
                    display_frame
                )
            # 10. 键盘
            key = cv2.waitKey(1) & 0xFF
            # Q：退出
            if key == ord("q"):
                break
            # 按 s 保存当前帧
            # S：保存当前照片 + 骨架预览 + 当前关键点 JSON
            if key == ord("s"):
                snapshot_name = time.strftime(
                    "%Y%m%d_%H%M%S"
                )
                snapshot_dir = (
                        output_dir
                        / f"snapshot_{snapshot_name}"
                )
                snapshot_dir.mkdir(
                    parents=True,
                    exist_ok=True
                )
                snapshot_data = {
                    "timestamp": snapshot_name,
                    "cameras": []
                }
                for i, frame in enumerate(frames):
                    # 1. 保存原始照片
                    raw_path = (
                            snapshot_dir
                            / f"camera_{i}_raw.jpg"
                    )
                    cv2.imwrite(
                        str(raw_path),
                        frame
                    )
                    # 2. 保存带骨架的预览图
                    preview_frame = frame.copy()
                    preview_frame = draw_hand_skeleton(
                        preview_frame,
                        all_hands[i]
                    )
                    preview_path = (
                            snapshot_dir
                            / f"camera_{i}_skeleton.jpg"
                    )
                    cv2.imwrite(
                        str(preview_path),
                        preview_frame
                    )
                    # 3. 保存这一台摄像头的关键点
                    camera_data = {
                        "camera_id": i,
                        "image_width": frame.shape[1],
                        "image_height": frame.shape[0],
                        "hands": all_hands[i]
                    }
                    snapshot_data["cameras"].append(
                        camera_data
                    )
                # 4. 写入 JSON
                json_path = (
                        snapshot_dir
                        / "keypoints.json"
                )
                with open(
                        json_path,
                        "w",
                        encoding="utf-8"
                ) as f:
                    json.dump(
                        snapshot_data,
                        f,
                        ensure_ascii=False,
                        indent=4
                    )
                print(
                    f"截图已保存：{snapshot_dir}"
                )
            if key == ord("r"):
                # 开始录制
                if not recording:
                    # 每一次按 R 都生成新的 session
                    session_name = time.strftime(
                        "%Y%m%d_%H%M%S"
                    )
                    session_dir = (
                        output_dir
                        / session_name
                    )
                    session_dir.mkdir(
                        parents=True,
                        exist_ok=True
                    )
                    writers = []
                    # 每个摄像头创建一个视频文件
                    for i, frame in enumerate(frames):
                        height, width = frame.shape[:2]
                        filename = (
                            session_dir
                            / f"camera_{i}.mp4"
                        )
                        fourcc = (
                            cv2.VideoWriter_fourcc(
                                *"mp4v"
                            )
                        )
                        writer = cv2.VideoWriter(
                            str(filename),
                            fourcc,
                            30.0,
                            (width, height)
                        )
                        writers.append(writer)
                    # 创建关键点 JSONL
                    keypoint_writer = KeypointWriter(
                        session_dir
                        / "keypoints.jsonl"
                    )
                    frame_id = 0
                    recording_start_time = (
                        time.perf_counter()
                    )
                    recording = True
                    print(
                        f"开始采集：{session_dir}"
                    )
                # 停止录制
                else:
                    recording = False
                    for writer in writers:
                        writer.release()
                    writers = []
                    if keypoint_writer is not None:
                        keypoint_writer.close()
                    keypoint_writer = None
                    print("采集结束")
    finally:
        # 11. 程序退出时清理资源
        for backend in pose_backends:
            backend.close()
        for writer in writers:
            writer.release()
        if keypoint_writer is not None:
            keypoint_writer.close()
        for camera in cameras:
            camera.release()
        cv2.destroyAllWindows()
if __name__ == "__main__":
    main()