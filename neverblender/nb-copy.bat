@echo off

rem * Copies the script files to Blender directory.
rem * This .bat was mostly made due to fact that I tend to need to 
rem * edit the files often, and Win98SE / FAT32 doesn't support this
rem * advanced feature known as "symlinks". To use this on non-Finnish
rem * Windows installations, or where Blender is installed elsewhere,
rem * you need to edit the script.

set NBPATH="c:\Ohjelmatiedostot\Blender Foundation\Blender\.blender\scripts"
echo Copying files to %NBPATH%
xcopy nwnmdl*.py %NBPATH%

