@ECHO OFF

 
:INPUT_START
ECHO;
ECHO +-------------------------------------------------------+
ECHO  �������镶������͂��Ă��������B
ECHO +-------------------------------------------------------+
ECHO;
SET INPUT_STR=
SET /P INPUT_STR=
 
IF "%INPUT_STR%"=="" GOTO :INPUT_START
 
:INPUT_CONF
ECHO;
ECHO +-------------------------------------------------------+
ECHO  ���͂���������[%INPUT_STR%]�ł�낵���ł����H
ECHO �iY / N�j
ECHO +-------------------------------------------------------+
ECHO;
SET CONF_SELECT=
SET /P CONF_SELECT=
 
IF "%CONF_SELECT%"== SET CONF_SELECT=Y
IF /I NOT "%CONF_SELECT%"=="Y"  GOTO :INPUT_START

python main.py "%INPUT_STR%" "m6QErb DxyBCb kA9KIf dS8AEf ecceSd" "hfpxzc"
ECHO;
pause