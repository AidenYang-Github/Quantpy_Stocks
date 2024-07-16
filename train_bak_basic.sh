#!/bin/bash
cur_path=D:/A_Skateboy_S/Python/knowledge_archive-master/Collections/Stocks

func='bak_basic'
DATE=`date "+%Y-%m-%d_%H-%M-%S"`

python $cur_path/mysql_stock.py \
		--function=${func} >> ${func}_${DATE}.log 2>&1

echo "Shell Done!"

exec /bin/bash