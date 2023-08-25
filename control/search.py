# -*- coding:utf-8 -*-
'''
360도 탐색 코드 
느린속도로 60도씩 돌리기 
멈추기
'''

import Jetson.GPIO
from adafruit_servokit import ServoKit  # 모터 드라이버 라이브러리
import time     # sleep 함수 라이브러리
import board        # 보드 핀 출력 시 필요
import busio
import digitalio    # 보드 핀 출력 시 필요

i2c_bus0=(busio.I2C(board.SCL_1, board.SDA_1))  # I2C 0번 버스 사용, SDA,SCL 27,28번 핀
myKit=ServoKit(i2c=i2c_bus0, channels=16) # 모터 드라이버 채널 개수:16개 설정


# 불 감지 하기 위해 계속 탐색 하는 코드
# angle이 90이면 정지, 90에 가까울수록 느려지고,
# 90보다 낮으면 시계방향 회전, 90보다 높으면 반시계방향으로 회전

myKit.servo[0].angle=86.5   # 360도 모터를 86.5의 속도로 시계방향 회전
print("86.5") 
time.sleep(1.33)            # 60도 정도 각도가 되는 시간 만큼 회전     
myKit.servo[0].angle=90     # 360도 모터 정지
print("90")
time.sleep(1)               # 1초 

    