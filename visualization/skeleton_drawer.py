import cv2
# MediaPipe 21 个手部点的连线关系
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),

    (0, 5), (5, 6), (6, 7), (7, 8),

    (5, 9), (9, 10), (10, 11), (11, 12),

    (9, 13), (13, 14), (14, 15), (15, 16),

    (13, 17), (17, 18), (18, 19), (19, 20),

    (0, 17)
]
def draw_hand_skeleton(frame, hands):
    for hand in hands:
        points = hand["points"]
        # 1. 画骨骼线
        for start_id, end_id in HAND_CONNECTIONS:
            start = points[start_id]
            end = points[end_id]
            cv2.line(
                frame,
                (start["x"], start["y"]),
                (end["x"], end["y"]),
                (0, 255, 0),
                2
            )
        # 2. 画关键点
        for point in points:
            x = point["x"]
            y = point["y"]
            cv2.circle(
                frame,
                (x, y),
                5,
                (0, 0, 255),
                -1
            )
            # 显示点编号
            cv2.putText(
                frame,
                str(point["id"]),
                (x + 5, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255),
                1
            )
    return frame