python -OO -m
PyInstaller -w ^
--onefile ^
-i saturn.ico ^
--distpath "./Build/WindowsNoEditor" ^
--workpath "./Saved/Build" ^
main.py

robocopy test Build/WindowsNoEditor/test /E