class LandmarkSmoother:
    def __init__(self, alpha=0.5):
        self.alpha = alpha
        # 分别保存左手、右手上一帧的数据
    def smooth(self, hands):
        # 当前一只手都没检测到
        if not hands:
            return []
        smoothed_hands = []
        self.previous_hands = {}
        current_keys = set()
        for hand_index, hand in enumerate(hands):
            # 优先用 Left / Right 区分两只手
            handedness = hand.get("handedness")
            if handedness is not None:
                key = handedness
            else:
                # 万一没有左右手标签，就暂时按顺序区分
                key = f"hand_{hand_index}"
            current_keys.add(key)
            new_points = hand["points"]
            # 这只手上一帧存在
            if key in self.previous_hands:
                old_hand = self.previous_hands[key]
                old_points = old_hand["points"]
                smoothed_points = []
                for old, new in zip(
                    old_points,
                    new_points
                ):
                    # EMA平滑
                    a = self.alpha
                    x = (
                            a * new["x"]
                            + (1 - a) * old["x"]
                    )
                    y = (
                            a * new["y"]
                            + (1 - a) * old["y"]
                    )
                    z = (
                            a * new["z"]
                            + (1 - a) * old["z"]
                    )
                    smoothed_points.append({
                        **new,
                        "x": int(x),
                        "y": int(y),
                        "z": float(z)
                    })
                smoothed_hand = {
                    **hand,
                    "points": smoothed_points
                }
            # 第一次检测到这只手
            else:
                smoothed_hand = hand
            self.previous_hands[key] = smoothed_hand
            smoothed_hands.append(
                smoothed_hand
            )
        # 删除这一帧已经消失的手
        disappeared = (
            set(self.previous_hands.keys())
            - current_keys
        )
        for key in disappeared:
            del self.previous_hands[key]
        return smoothed_hands