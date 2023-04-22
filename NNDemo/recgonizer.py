from hoshino import Service
import aiohttp
import asyncio
from threading import Thread
import cv2
import numpy as np
import os
from os import path

sv_help='''
--------v0.1---------
目前仅支持用pjjc的战绩页面来查
其他图片一概不支持
如果有角色查询错误，大概率是因为数据库没有录入该角色，请联系作者
'''.strip()
sv = Service('图片拆', bundle='pjjc图片查询', help_=sv_help)
_dir = path.dirname(__file__)+"/"


async def download(url):
    try:
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                content = await resp.read()
                return content
    except:
        return False

# 读取数据集
def loadset():
    global imgs
    for file in os.listdir(_dir + 'dataset/'):
        temp = cv2.imread(f'{_dir}dataset/{file}', 0)
        imgs.append(cv2.resize(temp, (bit, bit)))
        imgnames.append(file[:-4])

# 头像识别
def recgonize():
    resnames = []
    for i in range(10):
        image2 = cv2.imread(f'{_dir}testset/{i+1}.jpg', 0)
        image2 = cv2.resize(image2, (bit, bit))
        maxans = 0
        maxi = 0
        for k, img in enumerate(imgs):
            image1 = imgs[k]
            difference = image1 - image2
            ans = 0
            for i in range(int(bit*0.2), int(bit*0.8)):
                for j in range(int(bit*0.2), int(bit*0.8)):
                    if (difference[i, j] <= 10):
                        ans += 1
            if maxans < ans:
                maxi = k
                maxans = ans
        resnames.append(imgnames[maxi])
        # print(maxans)
    return resnames

def getavatars(img):
    grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, reduced_img = cv2.threshold(grey_img, 127, 255, cv2.THRESH_TOZERO)
    contour, hierarchy = cv2.findContours(reduced_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    perimeter = cv2.arcLength(contour[0], True)  # 计算轮廓周长
    approx = cv2.approxPolyDP(contour[0], 0.1 * perimeter, True)  # 获取轮廓角点坐标
    x, y, w, h = cv2.boundingRect(approx)  # 获取坐标值和宽度、高度
    avatars = [[0, 0, 0, 0] for i in range(10)]  # 10个头像的x,y,w,h
    wgap = 0
    hgap = h * 0.224
    for i in range(5):
        avatars[i + 5][0] = avatars[i][0] = int(w * 0.48 + x + wgap)  # x0
        avatars[i][1] = int(h * 0.255 + y)  # y0
        avatars[i + 5][1] = int(avatars[i][1] + hgap)
        avatars[i + 5][2] = avatars[i][2] = int(avatars[i][0] + w * 0.07)  # x1
        avatars[i][3] = int(avatars[i][1] + h * 0.13)  # y1
        avatars[i + 5][3] = int(avatars[i][3] + hgap)
        wgap += w * 0.07436
    for i in range(10):
        cv2.imwrite(f'{_dir}testset/{i + 1}.jpg', img[avatars[i][1]:avatars[i][3], avatars[i][0]:avatars[i][2]])
        # avatars[i][0]:avatars[i][2] avatars[i][1]:avatars[i][3]



@sv.on_prefix(('拆一哈'))
async def carryover_cal(bot, ev):
    global bit
    global imgs
    global imgnames
    bit = 32
    imgs = []
    imgnames = []
    loadset()
    content = ev.message
    img_url = content[0]["data"].get("url")
    if img_url == None:
        await bot.send(ev, '未检测到图片')
        return
    p = await download(img_url)
    img = cv2.imdecode(np.frombuffer(p, np.uint8), cv2.IMREAD_COLOR)
    # temp_file = f'battlepic/battle.jpg'
    # cv2.imwrite(temp_file, img)
    # img = cv2.imread('battlepic/battle.jpg')
    getavatars(img)
    results = recgonize()
    await bot.send(ev,f'怎么拆{results[0]}{results[1]}{results[2]}{results[3]}{results[4]}')
    await bot.send(ev, f'怎么拆{results[5]}{results[6]}{results[7]}{results[8]}{results[9]}')

