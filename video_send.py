#coding:utf-8
import time
import cv2
import paramiko
import os
import dlib
import numpy as np
import glob

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'


def mp4vTox264(fin):
    #fin="/home/pi/car_app/xuxin/0.mp4"
    file=fin.split("/")[-1]
    fileNum=file.split(".")[0]
    fdir=fin[:len(fin)-len(file)]
    fout=fdir+fileNum+"h.mp4"
    res=os.popen("ffmpeg -i {0} -codec libx264 {1} -y".format(fin,fout))
    
font = cv2.FONT_HERSHEY_SIMPLEX
cap = cv2.VideoCapture(0)
cap.set(3, 480)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
_fps = 18   
print('ok')
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
ip = '49.234.112.124'
port = '22'
user = 'root'
password = 'Transience1896'
flag = True
pic_idx = 0
vid_idx = 0

while (1):
    fff = open(device_file , 'r')
    lines = fff.readlines()
    fff.close()
    temp = lines[1][-6:-1]
    temp = float(temp)/1000.
    ret, frame = cap.read()
    wd = frame.shape[0]
    lg = frame.shape[1]
    frame = cv2.resize(frame,(lg/4,wd/4))
    img = frame[100:,:]
    img[img is not 255] = 255
    frame = cv2.vconcat((frame,img),dst = None)
    cv2.putText(frame, "t = {}".format(temp), (0, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 0, 255), 2, 4)
    img_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    rects = detector(img_gray, 0)
    if (len(rects) != 0):

        for i in range(len(rects)):
            for k, d in enumerate(rects):
                cv2.rectangle(frame, (d.left(), d.top()), (d.right(), d.bottom()), (0, 0, 255))
                face_width = d.right() - d.left()
                face_higth = d.top() - d.bottom()
                shape = predictor(frame, d)
                mouth_width = (shape.part(54).x - shape.part(48).x) / face_width
                mouth_higth = (shape.part(66).y - shape.part(62).y) / face_width
                brow_sum = 0
                frown_sum = 0
                for j in range(17, 21):
                    brow_sum += (shape.part(j).y - d.top()) + (shape.part(j + 5).y - d.top())
                    frown_sum += shape.part(j + 5).x - shape.part(j).x
                    line_brow_x.append(shape.part(j).x)
                    line_brow_y.append(shape.part(j).y)
    
                tempx = np.array(line_brow_x)
                tempy = np.array(line_brow_y)
                z1 = np.polyfit(tempx, tempy, 1)
                brow_k = -round(z1[0], 3)
                brow_hight = (brow_sum / 10) / face_width
                brow_width = (frown_sum / 5) / face_width
            
                eye_sum = (shape.part(41).y - shape.part(37).y + shape.part(40).y - shape.part(38).y + shape.part(
                    47).y - shape.part(43).y + shape.part(46).y - shape.part(44).y)
                eye_hight = (eye_sum / 4) / face_width
    
                if round(mouth_higth >= 0.03):
                    if eye_hight >= 0.056:
                        cv2.putText(frame, "amazing", (5, 100), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.4,
                                    (0, 0, 255), 2, 4)
                    else:
                        cv2.putText(frame, "happy", (5, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                                    (0, 0, 255), 2, 4)
            
            
                else:
                    if brow_k <= -0.3:
                        cv2.putText(frame, "angry", (5, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                                    (0, 0, 255), 2, 4)
                    else:
                        cv2.putText(frame, "nature", (5, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                                    (0, 0, 255), 2, 4)  
        #cv2.putText(frame, "Faces: " + str(len(rects)), (20, 50), font, 1, (0, 0, 255), 1, cv2.LINE_AA)
    else:
        cv2.putText(frame, "No Face", (5, 100), font, 0.4, (0, 0, 255), 1, cv2.LINE_AA)
    
    
    
    
    wd = wd/4+20
    lg = lg/4
    line_brow_x = []
    line_brow_y = []
    if flag:
        if os.path.exists('/home/pi/Desktop/{}.mp4'.format(vid_idx)): 
            os.remove('/home/pi/Desktop/{}.mp4'.format(vid_idx))
        videoWriter = cv2.VideoWriter('/home/pi/Desktop/{}.mp4'.format(vid_idx), fourcc, _fps, (lg,wd))   #(1360,480)
        local_file = '/home/pi/Desktop/{}.mp4'.format(vid_idx)
        local_file2 = '/home/pi/Desktop/{}h.mp4'.format(vid_idx)
        remote_file = '/home/wwwroot/default/car/h264/{}.mp4'.format(vid_idx)
        flag = False
        vid_idx += 1
        vid_idx = vid_idx%2
    pic_idx += 1
    if pic_idx % 50 is not 0:
        videoWriter.write(frame)
    else:
        videoWriter.release()
        pic_idx = 0
        mp4vTox264(local_file)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, user, password)
        sftp = ssh.open_sftp()
        sftp.put(local_file2, remote_file)
        flag = True
        print('sending',local_file2)

