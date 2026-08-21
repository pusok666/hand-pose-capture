import math
def calculate_angle(a, b, c):
    """
    计算 ∠ABC
    b 是中间点
    """
    ba_x = a["x"] - b["x"]
    ba_y = a["y"] - b["y"]
    bc_x = c["x"] - b["x"]
    bc_y = c["y"] - b["y"]
    dot = ba_x * bc_x + ba_y * bc_y
    len_ba = math.sqrt(
        ba_x ** 2 + ba_y ** 2
    )
    len_bc = math.sqrt(
        bc_x ** 2 + bc_y ** 2
    )
    if len_ba == 0 or len_bc == 0:
        return None
    cos_angle = dot / (len_ba * len_bc)
    # 防止浮点误差导致 acos 越界
    cos_angle = max(
        -1.0,
        min(1.0, cos_angle)
    )

    angle = math.degrees(
        math.acos(cos_angle)
    )
    return angle
def get_index_finger_angles(points):
    """
    MediaPipe 食指:
    5 = MCP
    6 = PIP
    7 = DIP
    8 = TIP
    """
    pip_angle = calculate_angle(
        points[5],
        points[6],
        points[7]
    )
    dip_angle = calculate_angle(
        points[6],
        points[7],
        points[8]
    )
    return {
        "pip_angle": pip_angle,
        "dip_angle": dip_angle
    }
def distance(a, b):
    return math.sqrt(
        (a["x"] - b["x"]) ** 2
        +
        (a["y"] - b["y"]) ** 2
    )
def calculate_hand_openness(points):
    """
    用五个指尖到掌心的距离，
    粗略估计手掌张开程度。
    """
    # 用 0、5、9、13、17 附近平均作为掌心
    palm_ids = [0, 5, 9, 13, 17]
    palm_x = sum(
        points[i]["x"]
        for i in palm_ids
    ) / len(palm_ids)
    palm_y = sum(
        points[i]["y"]
        for i in palm_ids
    ) / len(palm_ids)
    palm = {
        "x": palm_x,
        "y": palm_y
    }
    fingertip_ids = [
        4,   # 拇指
        8,   # 食指
        12,  # 中指
        16,  # 无名指
        20   # 小指
    ]
    distances = [
        distance(
            points[i],
            palm
        )
        for i in fingertip_ids
    ]
    average_distance = (
        sum(distances)
        / len(distances)
    )
    # 用掌宽归一化
    palm_width = distance(
        points[5],
        points[17]
    )
    if palm_width == 0:
        return None
    openness = (
        average_distance
        / palm_width
    )
    return openness
def analyze_hand(hand):
    points = hand["points"]
    index_angles = (
        get_index_finger_angles(points)
    )
    openness = (
        calculate_hand_openness(points)
    )
    return {
        "index_pip_angle":
            index_angles["pip_angle"],
        "index_dip_angle":
            index_angles["dip_angle"],
        "hand_openness":
            openness
    }