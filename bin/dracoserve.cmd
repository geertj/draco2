@echo off

:again
draco.py serve -s %1 %2 %3 %4
goto again
