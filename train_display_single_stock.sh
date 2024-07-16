#!/bin/bash
cur_path=D:/A_Skateboy_S/Python/knowledge_archive-master/Collections/Stocks
stock_code='601882.SH'
echo 'ts code is '${stock_code}
python $cur_path/mysql_data_processing.py \
		--num=0 \
		--stock_code=${stock_code} \
		--function=1

sleep 10

#603167.SH