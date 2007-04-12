@echo off
rem Windows seems to have a per user temp directory, so a
rem fixed temp file name should not be a security issue.
set tempfile=%TEMP%\tempenv.cmd
python env.py >%tempfile%
call %tempfile%
del %tempfile%
