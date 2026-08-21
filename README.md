# Hand Pose Capture

基于 OpenCV 和 MediaPipe 的实时手部关键点采集与可视化原型。

## 当前功能

- 摄像头实时采集
- 支持多摄像头扩展
- MediaPipe Hand Landmarker 21 点检测
- 实时手部骨架可视化
- EMA 关键点平滑
- 食指 PIP / DIP 角度计算
- 手掌张开度计算
- 按 `S` 保存：
  - 原始图片
  - 骨架预览图
  - 关键点 JSON
- 按 `R` 保存：
  - 原始视频
  - 逐帧关键点 JSONL
- 按 `Q` 退出程序

## 项目结构

```text
hand-pose-capture/
├── capture/
├── pose/
├── storage/
├── visualization/
├── models/
├── output/
├── main.py
└── requirements.txt
```

## 安装

```bash
pip install -r requirements.txt
```

## 模型

程序使用 MediaPipe Hand Landmarker 模型。

请将模型文件放到：

```text
models/hand_landmarker.task
```

模型文件默认不会上传到 GitHub，需要单独下载后放入该目录。

## 操作

```text
S  保存当前截图、骨架预览和关键点 JSON
R  开始 / 停止录像，并保存逐帧关键点 JSONL
Q  退出程序
```

## 输出数据

截图模式会生成类似：

```text
output/
└── snapshot_20260821_164800/
    ├── camera_0_raw.jpg
    ├── camera_0_skeleton.jpg
    └── keypoints.json
```

录像模式会生成类似：

```text
output/
└── 20260821_165000/
    ├── camera_0.mp4
    └── keypoints.jsonl
```

## 当前状态

目前为手部姿态数据采集与可视化原型。

当前重点是稳定获取手部关键点和基础几何特征，后续可根据实际需求继续扩展：

- 固定机位数据采集
- 多摄像头同步
- 更多手部几何特征
- 专家标注数据对齐
- 姿态分类
- 时序动作分析