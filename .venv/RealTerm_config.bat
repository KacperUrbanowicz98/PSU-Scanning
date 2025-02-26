@echo off
start "" "C:\Program Files (x86)\BEL\Realterm\realterm.exe" /C=COM7 /B=115200 /D=8 /S=1 /P=none /ROWS=80 /COLS=80 /EOL=+CR+LF+CR /SEND=AT+HELP
