#!/usr/bin/python3
# coding=utf8

import sys
import time
import cv2
import mediapipe as mp

import hiwonder.Camera as Camera
import hiwonder.ActionGroupControl as AGC
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller
import hiwonder.yaml_handle as yaml_handle

# =============== 云台参数（你说 1500 是中位） ===============
YAW_ID = 2    # 水平
PITCH_ID = 1  # 俯仰

YAW_CENTER = 1500
PITCH_CENTER = 1500

YAW_MIN, YAW_MAX = 1100, 1900
PITCH_MIN, PITCH_MAX = 1200, 1900

# 像素误差 -> 脉宽变化 的比例（关键）
# 数值越大转得越快，建议先用这个稳一点
K_YAW = 0.05
K_PITCH = 0.01

# 回中速度（0~1，越大回得越快）
RETURN_ALPHA = 0.03

# 每次控制的最短间隔
DT = 0.02

# 人脸检测阈值
MIN_CONF = 0.6

# 若你的云台方向相反，改这里
INVERT_YAW = False      # True 会反向水平
INVERT_PITCH = True     # 很多云台俯仰方向需要反一下（你之前“低头”的概率也在这）

# =============== 基础检查 ===============
if sys.version_info.major == 2:
    print("Please run this program with python3!")
    sys.exit(0)

# =============== 读取配置（仅用于相机 open_once，不再用 servo_data 做中位） ===============
try:
    open_once = yaml_handle.get_yaml_data('/boot/camera_setting.yaml')['open_once']
except Exception:
    open_once = False

# =============== 初始化底层控制 ===============
board = rrc.Board()
ctl = Controller(board)

def clamp(v, vmin, vmax):
    return vmin if v < vmin else vmax if v > vmax else v

def gimbal_move(yaw_pulse, pitch_pulse, ms=80):
    yaw_pulse = int(clamp(yaw_pulse, YAW_MIN, YAW_MAX))
    pitch_pulse = int(clamp(pitch_pulse, PITCH_MIN, PITCH_MAX))
    ctl.set_pwm_servo_pulse(YAW_ID, yaw_pulse, ms)
    ctl.set_pwm_servo_pulse(PITCH_ID, pitch_pulse, ms)

def initMove():
    # 直接回到 1500/1500（你认定的中心）
    gimbal_move(YAW_CENTER, PITCH_CENTER, ms=500)
    time.sleep(0.6)

# =============== MediaPipe 人脸检测 ===============
mp_face = mp.solutions.face_detection
face_detector = mp_face.FaceDetection(
    model_selection=0,
    min_detection_confidence=MIN_CONF
)

def main():
    print("Face Gimbal Tracking Start")
    initMove()
    AGC.runActionGroup('stand')

    # 相机
    if open_once:
        cam = cv2.VideoCapture('http://127.0.0.1:8080/?action=stream')
    else:
        cam = Camera.Camera()
        cam.camera_open()

    # 当前脉宽
    yaw = YAW_CENTER
    pitch = PITCH_CENTER

    last_print = time.time()

    try:
        while True:
            ret, img = cam.read()
            if img is None:
                time.sleep(0.01)
                continue

            h, w = img.shape[:2]
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            res = face_detector.process(rgb)

            if not res.detections:
                # ========== 没人脸：缓慢回中 ==========
                print("no face")
                yaw += (YAW_CENTER - yaw) * RETURN_ALPHA
                pitch += (PITCH_CENTER - pitch) * RETURN_ALPHA
                gimbal_move(yaw, pitch, ms=80)
                time.sleep(DT)
                continue

            # ========== 有人脸：取第一个检测框 ==========
            det = res.detections[0]
            bbox = det.location_data.relative_bounding_box

            cx = (bbox.xmin + bbox.width * 0.5) * w
            cy = (bbox.ymin + bbox.height * 0.5) * h

            err_x = cx - (w * 0.5)  # 右为正
            err_y = cy + (h * 0.1)  # 下为正

            # 像素误差 -> 脉宽增量
            dyaw = (-err_x * K_YAW)
            dpitch = (-err_y * K_PITCH)

            if INVERT_YAW:
                dyaw = -dyaw
            if INVERT_PITCH:
                dpitch = -dpitch

            yaw += dyaw
            pitch += dpitch

            yaw = clamp(yaw, YAW_MIN, YAW_MAX)
            pitch = clamp(pitch, PITCH_MIN, PITCH_MAX)

            # 运动时间按误差大小给个自适应，避免抖
            move_delta = max(abs(dyaw), abs(dpitch))
            ms = int(clamp(60 + move_delta * 0.3, 60, 250))

            gimbal_move(yaw, pitch-200, ms=ms)

            # 打印观察：确认俯仰是否真的在变
            if time.time() - last_print > 1.0:
                last_print = time.time()
                print(f"face center=({int(cx)},{int(cy)}) yaw={int(yaw)} pitch={int(pitch)}")

            time.sleep(DT)

    except KeyboardInterrupt:
        print("Exit")

    finally:
        try:
            gimbal_move(YAW_CENTER, PITCH_CENTER, ms=400)
        except Exception:
            pass

        if open_once:
            cam.release()
        else:
            cam.camera_close()

if __name__ == "__main__":
    main()
