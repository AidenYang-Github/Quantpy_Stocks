#!/bin/bash
cur_path=D:/A_Skateboy_S/Python/knowledge_archive-master/Collections/Stocks
log_path=D:/A_Skateboy_S/Stock_related/stocks_log
DATE=`date "+%Y-%m-%d_%H-%M-%S"`

echo 'Date ' ${DATE}

python $cur_path/mysql_stock.py >> ${log_path}/train_${DATE}.txt 2>&1

echo "Shell Done!"

exec /bin/bash