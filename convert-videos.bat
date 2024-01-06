:: Set paths first before running!!!
set video_path="\app\WindowsNoEditor\Mercury\Content\Movie"
set export_path=".\data\movies"

for %%i in (%video_path%\*.usm) do ffmpeg -f mpegvideo -i "%%i" "%export_path%\%%~ni.mp4"