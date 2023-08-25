#!/usr/bin/python3
# -*- coding:utf-8 -*-

'''
복합 제어 코드 
1. motor 조준 코드 
2. water pump 코드 
3. 텔레그램 코드 
'''

import asyncio
import telegram
from datetime import datetime
from adafruit_servokit import ServoKit  # 모터 드라이버 라이브러리
import time                             # sleep 함수 라이브러리
import board                            # 보드 핀 출력 시 필요
import busio
import digitalio                        # 보드 핀 출력 시 필요
from PIL import Image

i2c_bus0=(busio.I2C(board.SCL_1, board.SDA_1))  # I2C 0번 버스 사용, SDA,SCL 27,28번 핀
myKit=ServoKit(i2c=i2c_bus0, channels=16) # 모터 드라이버 채널 개수:16개 설정

offset = 20 # 카메라 프레임의 중앙 기준 오프셋

motor = digitalio.DigitalInOut(board.D13)       # 릴레이 핀 위치 33번 핀
motor.direction = digitalio.Direction.OUTPUT    # 릴레이 핀을 출력을 설정

# 텔레그램 기본 정보 
token = "6600582276:AAHo4Ub-NxWFup6wbJMDgRXrA520smylDzE"
chat_id = '6690634597'
bot = telegram.Bot(token)
img_path = '/home/rolab/Bbox_coord/pic.jpg' #화재 캡처 파일 경로 

#텔레그램 비동기 메인함수
async def main():
    k = 0
    await fire()

#화재 함수
async def fire(): 
    now = datetime.now()
    accident_time = (
        str(now.year) + '년 ' + str(now.month) + '월 ' + str(now.day) + '일 \n'
        + str(now.hour) + '시 ' + str(now.minute) + '분 ' + str(now.second) + '초\n'
    )
    bot.send_message(chat_id=chat_id, text='--긴급 상황 안내--\n'+accident_time + '화재 발생')
    bot.send_photo(chat_id,photo=open(img_path,'rb'))
    asyncio.sleep(1)

#텍스트 열기 
f = open ("/home/rolab/Bbox_coord/Bbox.txt", "r")    # txt 파일 열기
reading = f.readline() # 텍스트 파일 첫줄 읽기, reading에 저장
judge = int(reading[0])
if judge == 0:
    time.sleep(1)
else:

    left_top_x = int(reading[1:5])  # 박스의 죄측 상단 x축 좌표 저장
    left_top_y = int(reading[6:10])  # 박스의 죄측 상단 y축 좌표 저장
    width  = int(reading[11:15])  # 박스의 죄측 상단 x축 좌표 저장
    height = int(reading[16:20])  # 박스의 죄측 상단 y축 좌표 저장

    print("left_top_x : ")
    print(left_top_x)
    print("left_top_y : ")
    print(left_top_y)
    print("width : ")
    print(width)
    print("height : ")
    print(height)

    center_x = (left_top_x + width)/2 
    center_y = (left_top_y + height)/2 

    print("center_x : ")
    print(center_x)

    print("center_y : ")
    print(center_y)

    # x 조준
    degree_per_pixel = 62.2/1280
    print("degree_per_pixel : ")
    print(degree_per_pixel)

    second_per_degree = 1.33/60
    print("second_per_degree : ")
    print(second_per_degree)

    # y 조준
    y_degree_per_pixel = 48.8/720
    print("y_degree_per_pixel : ")
    print(y_degree_per_pixel)

    ## 시간에 가중치 넣어서 코딩하기 

    myKit.servo[1].angle=45 # 180도 서보 모터 위치 초기화

    ## 시간에 가중치 넣어서 코딩하기 

    if center_x < (640 - offset): # 불이 화면 좌측에 존재, 620번째 픽셀 기준

        x_time = (640-center_x)*degree_per_pixel*second_per_degree
        print("x_time : ")
        print(x_time)

        myKit.servo[0].angle=86.5   # 360도 모터를 86.5의 속도로 시계방향 회전
        time.sleep(x_time)          # x_time동안 회전
        myKit.servo[0].angle=90     # 360도 모터 정지
        print("90")
        time.sleep(1)               # 1초간 정지

    elif center_x > (640 + offset): # 불이 화면 우측에 존재, 640번째 픽셀 기준
        x_time = (center_x-640)*degree_per_pixel*second_per_degree
        print("x_time : ")
        print(x_time)

        myKit.servo[0].angle=100.5   # 360도 모터를 100.5의 속도로 반시계방향 회전
        print("100.5") 
        time.sleep(3)               # x_time동안 회전

        myKit.servo[0].angle=90     # 360도 모터 정지
        print("90")
        time.sleep(1)               # 1초간 정지

    elif center_x > (640 - offset) and center_x < (640 + offset): # 불이 화면 중앙 주위에 존재
        
        myKit.servo[0].angle=90     # 360도 모터 정지
        print("90") 
        time.sleep(1)               # 1초간 정지

    myKit.servo[0].angle=90         # 360도 모터 정지
    print("90")
    time.sleep(3)                   # 정지

    # y 조준

    # 시간에 가중치 넣어서 코딩하기

    if center_y < (360 - offset):
        y_angle = 45-((360-center_y)*y_degree_per_pixel)
        myKit.servo[1].angle = y_angle
        print("y_angle : ")
        print(y_angle)

        motor.value = True  # 릴레이 활성화, 펌프 작동
        print("pump on")
        #텔레그램 전송
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())     
        time.sleep(3)       # 카메라에 따른 조건동안 true
        motor.value = False     # 릴레이 비활성화, 펌프 정지  
        print("pump off")       

    elif center_y > (360 + offset):
        y_angle = 45+((360+center_y)*y_degree_per_pixel)
        myKit.servo[1].angle = y_angle
        print("y_angle : ")
        print(y_angle)

        motor.value = True  # 릴레이 활성화, 펌프 작동
        print("pump on")
        #텔레그램 전송
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())     
        time.sleep(3)       # 카메라에 따른 조건동안 true
        motor.value = False     # 릴레이 비활성화, 펌프 정지  
        print("pump off")      

    elif center_y > (360 - offset) and center_y < (360 + offset): # 불이 화면 중앙 주위에 존재
        
        motor.value = True  # 릴레이 활성화, 펌프 작동
        print("pump on")
        #텔레그램 전송
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())     
        time.sleep(3)       # 카메라에 따른 조건동안 true
        motor.value = False     # 릴레이 비활성화, 펌프 정지  
        print("pump off")      

    myKit.servo[1].angle=45 