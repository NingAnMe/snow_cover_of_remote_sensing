#!/bin/bash
# 测试匹配模块所有程序

basepath=$(cd `dirname $0`; pwd)
cd $basepath
bashName=`basename $0`

#pnums=`ps x |grep -w $bashName |grep -v grep | wc -l`
#cfgName=`echo $bashName |awk -F '.' '{print $1}'`.cfg
#logName=`echo $bashName |awk -F '.' '{print $1}'`.log

cfgName=$1
binName=$2
jobs=`head -n 1 $cfgName`

let i=0
while read line 
do
    if [[ $i -eq 0 ]];then
        let i++
        continue
    fi
        # 跳过#开头行和空行
    if echo "$line"|grep -q -E "^$|^#"; then
        continue
    fi
    for job in $jobs
    do
        echo $line
        sat=`echo $line | awk '{print $1}'`
        times=`echo $line | awk '{print $2}'`
        #echo python3 ndsi_main.py -n $sat -j $job -t $times -c cfg/ndsi.cfg -p 0 -m 10 --rewrite --timeout 600 --visfile /RED1BDATA/cma/CALFILE/visfile.txt --irfile /RED1BDATA/cm/CALFILE/irfile.txt
        echo python3 ndsi_main.py -n $sat -j $job -t $times -c cfg/ndsi.cfg -p 0 -m 60 --rewrite --timeout 600 --version 1.0
        #python3 ndsi_main.py -n $sat -j $job -t $times -c cfg/ndsi.cfg -p 0 -m 60 --rewrite --timeout 600 --version 1.0

    done
done < $cfgName
