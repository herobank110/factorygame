Rem Go to the project root
cd ..\

IF EXIST ".\Saved\Build\WindowsNoEditor\main.spec" (
echo Found spec file directory
) ELSE (
echo Build spec file not found, run makespec.bat first
exit 1
)

Rem Copy icon to spec directory
copy skull.ico Saved\Build\WindowsNoEditor

python -O -m ^
 PyInstaller ^
--distpath "Build/WindowsNoEditor" ^
--workpath "Saved/Build/WindowsNoEditor/work" ^
"Saved/Build/WindowsNoEditor/main.spec"