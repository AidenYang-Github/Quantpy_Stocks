#!/bin/bash
cur_path=D:/A_Skateboy_S/Python/knowledge_archive-master/Collections/Stocks

echo "Date:" $(date +"%Y-%m-%d %H:%M:%S") 
func='train'
DATE=`date '+%Y-%m-%d_%H-%M-%S'`
echo 'func is '${func}
python ${cur_path}/test.py >> ${cur_path}/output/${func}_${DATE}.log 2>&1 

echo 'Shell done!'

exec /bin/bash