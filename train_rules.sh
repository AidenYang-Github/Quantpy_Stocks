#!/bin/bash
cur_path=D:/A_Skateboy_S/Python/knowledge_archive-master/Collections/Stocks
log_path=D:/A_Skateboy_S/Stock_related/stocks_log

train_file_name=rules

DATE=`date "+%Y-%m-%d_%H-%M-%S"`

echo 'Date ' ${DATE}

python $cur_path/${train_file_name}.py

echo "Shell Done!"

exec /bin/bash