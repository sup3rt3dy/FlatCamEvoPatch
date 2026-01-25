@echo off
setlocal
pushd "C:\\temp\\flatcam_beta_broken"
set "PATH=C:\\Users\\install\\miniconda3\\envs\\flatcam\Library\bin;C:\\Users\\install\\miniconda3\\envs\\flatcam\DLLs;C:\\Users\\install\\miniconda3\\envs\\flatcam\Scripts;C:\\Users\\install\\miniconda3\\envs\\flatcam;%SystemRoot%\system32;%SystemRoot%"
REM If needed on some GPUs, uncomment one of these:
REM set QT_OPENGL=angle & set QT_ANGLE_PLATFORM=d3d11
REM set QT_OPENGL=software & set LIBGL_ALWAYS_SOFTWARE=1
"C:\\Users\\install\\miniconda3\\envs\\flatcam\\python\.exe" flatcam.py
popd
endlocal
