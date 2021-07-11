#!/usr/bin/env python
# -*-coding:utf-8-*-
import os
import sys
import time
import stat
import zipfile
import shutil
import subprocess
import hashlib
import chardet
from collections import OrderedDict
import paramiko
from paramiko.ssh_exception import NoValidConnectionsError, AuthenticationException
from PIL import Image

reload(sys)
sys.setdefaultencoding('utf8')
# Const variables
SCAN_DIR = u'E:\\迅雷下载\\'
#SCAN_DIR = os.path.abspath('.')
# variables defines
current_encoding = 'GBK'


# file operation functions.
def RmTree(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            os.chmod(filename, stat.S_IWUSR)  # windows某些文件必须设置权限，否则删除失败
            os.remove(filename)
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(top)


# Make zip package function.
def MakeZip(source_dir, output_filename):
    zipf = zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED)
    pre_len = len(os.path.dirname(source_dir))
    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)  # relative path
            zipf.write(pathfile, arcname)
    zipf.close()


# SSH GET
def sftp_get(ip, user, pwd, local_file, remote_file, port=22):
    try:
        t = paramiko.Transport(ip, port)
        t.connect(username=user, password=pwd)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.get(remote_file, local_file)
        t.close()

    except Exception as e:
        print(e)


# SSH PUT
def sftp_put(ip, user, pwd, local_file, remote_file, port=22):
    try:
        t = paramiko.Transport(ip, port)
        t.connect(username=user, password=pwd)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.put(local_file, remote_file)
        t.close()

    except Exception as e:
        print(e)


# 该函数适合执行输出打印信息较少类型的命令，如果输出量大用该函数可能引发挂死
def CmdExcuteWithShortOutput(cmd, outFileName):
    cmd = cmd.encode('gbk')
    outFile = open(outFileName, 'a')
    popen = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             bufsize=1)

    # 重定向标准输出
    while popen.poll() is None:  # None表示正在执行中
        r = popen.stdout.readline()
        # print chardet.detect(r)
        r = r.decode(current_encoding)
        sys.stdout.write(r)  # 可修改输出方式，比如控制台、文件等
        # r = r.encode('gb2312')
        outFile.write(r)
        return r

        # r = popen.stdout.readline().decode(current_encoding)
        # sys.stdout.write(r)  # 可修改输出方式，比如控制台、文件等
        # outFile.write(r)

    # 重定向错误输出
    if popen.poll() != 0:  # 不为0表示执行错误
        err = popen.stderr.read().decode(current_encoding)
        sys.stdout.write(err)  # 可修改输出方式，比如控制台、文件等
        outFile.write(err)

    outFile.close()


# 该函数适合执行输出打印信息量大类型的命令，输出直接重定向到文件中，避免PIPE通道挂死。
def CmdExcuteWithLongOutput(cmd, outFileName):
    cmd = cmd.encode('gbk')
    print outFileName
    outFile = open(outFileName, 'a')
    outFile.write('Cmd is: ' + cmd + '\n')
    outFile.flush()
    popen = subprocess.Popen(cmd, shell=True, stdout=outFile, stderr=outFile)
    # while popen.poll() is None:         # None表示正在执行中
    popen.wait()
    outFile.close()


# 该函数与CmdExcuteWithLongOutput类似，利用communicate()函数读取输出，最后一次性写入文件
def CmdExcuteWithLongOutputOnceWrite(cmd, outFileName):
    cmd = cmd.encode('gbk')
    outFile = open(outFileName, 'a+')
    popen = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, )
    sout, serr = popen.communicate()
    outFile.write(sout)
    outFile.write(serr)
    outFile.flush()


def judge_file_type(file_name, file_type_list):
    if not file_name.endswith(file_type_list):
        return False
    return True


def judge_time_file(time_interval, file_time):
    current_time = time.mktime(time.localtime())
    # start_time = time.mktime(time.strptime('2020-04-12 00:00:00', "%Y-%m-%d %H:%M:%S"))
    # end_time  = time.mktime(time.strptime('2020-05-23 00:00:00', "%Y-%m-%d %H:%M:%S"))
    start_time = current_time - time_interval
    end_time = current_time
    # print(start_time , update_time , end_time)
    if start_time < file_time < end_time:
        return True
    return False


def get_preprocess_files(origin_path, file_type_list, time_interval):
    file_list = os.walk(origin_path)
    # for root, dirs, files in file_list:
    #    for d in dirs:
    #        print os.path.join(root, d)
    #    for f in files:
    #        print os.path.join(root, f)
    filter_file_list = []
    for root, dirs, files in file_list:
        for file_name in files:
            file_time = os.stat(os.path.join(root, file_name)).st_mtime
            if judge_file_type(file_name, file_type_list) and judge_time_file(time_interval, file_time):
                filter_file_list.append(os.path.join(root, file_name))
    # data_list.sort(key=lambda x: x[1])
    return filter_file_list


def get_video_duration(file_path):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
           file_path]
    cmd = ' '.join(cmd)
    res = CmdExcuteWithShortOutput(cmd, 'test.log')
    print res
    return float(res)


def ffmpeg_cmd_execute(cmd):
    cmd = cmd.encode('gbk')
    popen = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             bufsize=1)

    sout, serr = popen.communicate()
    print sout
    print serr


def image_concat(image_names, save_path):
    # image_names: list, 存放的是图片的绝对路径
    # 1.创建一块背景布
    image = Image.open(image_names[0])
    width, height = image.size
    target_shape = (3 * width, 3 * height)
    background = Image.new('RGBA', target_shape, (0, 0, 0, 0,))

    # 2.依次将图片放入背景中(注意图片尺寸规整、mode规整、放置位置)
    for ind, image_name in enumerate(image_names):
        img = Image.open(image_name)
        img = img.resize((width, height))  # 尺寸规整
        if img.mode != "RGBA":  # mode规整
            img = img.convert("RGBA")
        row, col = ind // 3, ind % 3
        location = (col * width, row * height)  # 放置位置
        background.paste(img, location)

    image_path = os.path.join(save_path, 'snapshot.png')
    background.save(image_path)


def rm_files_list(files_list):
    for file_path in files_list:
        os.chmod(file_path, stat.S_IWUSR)  # windows某些文件必须设置权限，否则删除失败
        os.remove(file_path)


def get_video_snapshot(files_list):
    for file_path in files_list:
        dir_name = os.path.dirname(file_path)
        dir_path = os.path.abspath(dir_name)
        duration = get_video_duration(file_path)
        snap_interval = duration / 10
        snap_time = 0
        for i in range(0, 9):
            snap_time = snap_time + snap_interval
            print snap_time
            pic_name = str(i) + '.jpg'
            pic_path = os.path.join(dir_path, pic_name)
            print pic_path
            # -ss参数必须放到-i之前，否则截图时ffmpeg会优先从头开始连续读视频流，读到指定时间点才截图，导致截图速度特别慢
            # Use -qscale:v (or the alias -q:v) as an output option. Effective range for JPEG is 2-31 with 31 being the worst quality. 
            cmd = ' '.join(
                ['ffmpeg -y', '-ss', str(snap_time), ' -i', file_path, '-qscale:v 15 -vframes 1', '-f image2', pic_path])
            print 'cmd: ' + cmd
            ffmpeg_cmd_execute(cmd)

        time.sleep(1)
        pic_list = get_preprocess_files(dir_path, '.jpg', 10800)
        image_concat(pic_list[:9], dir_path)
        rm_files_list(pic_list)


def main():
    origin_path = os.path.abspath(SCAN_DIR)
    file_type_list = ('.mp4', '.mkv')
    filter_file_list = get_preprocess_files(origin_path, file_type_list, 10800)
    get_video_snapshot(filter_file_list)


if __name__ == '__main__':
    main()
