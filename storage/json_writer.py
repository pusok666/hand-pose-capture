import json


class KeypointWriter:
    def __init__(self, file_path):
        self.file = open(
            file_path,
            "w",
            encoding="utf-8"
        )

    def write(
        self,
        frame_id,
        timestamp_ms,
        camera_id,
        hands
    ):
        record = {
            "frame_id": frame_id,
            "timestamp_ms": timestamp_ms,
            "camera_id": camera_id,
            "hands": hands
        }
        self.file.write(
            json.dumps(
                record,
                ensure_ascii=False
            )
            + "\n"
        )
        # 第一版直接刷新，避免程序突然结束导致数据没写进去
        self.file.flush()
    def close(self):
        if self.file:
            self.file.close()