import subprocess
import os

fhome="/home/wwwroot/default/car/"
for i in range(10):
    fin=fhome+"mp4v/{0}.mp4".format(i)
    fout=fhome+"h264/{0}.mp4".format(i)
    cmd ="ffmpeg -i {0} -codec libx264 {1}".format(fin,fout)
    res=os.popen(cmd)