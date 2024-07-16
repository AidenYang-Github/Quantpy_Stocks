#!/bin/bash

#D:\A_Skateboy_S\Python\knowledge_archive-master\Collections\Stocks>python mysql_data_processing.py

#当前路径
cur_path=D:/A_Skateboy_S/Python/knowledge_archive-master/Collections/Stocks
#cur_path=chdir

#cd $cur_path

python $cur_path/mysql_data_processing.py \
		--num=0 \
		--stock_code='300964.SZ'
		#--stock_code='sh601688' >> $cur_path/output/train.log 2>&1

sleep 10
#> ${cur_path}/output/train.log 2>&1
#> $cur_path/output/train.log 2>&1
	
#python mysql_data_processing.py \
		--num=100 
		
#'sh600519'
#sh688169	石头
#sh688696	极米

