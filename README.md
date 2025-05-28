一、本电子节目单（EPG）含央视，卫视，福建，数字频道等119个频道，频道的准确名称见channels.txt


二、每日从移动机顶盒接口抓取明天和后天的epg数据，生成两个文件，文件名格式为epg_yyyymmdd.xml


三、将超过9天的数据删除（即7天以前）


四、将9天的历史数据（含明后天）合并为all.xml并打包为all.xml.gz，地址：https://epg.136605.xyz/all.xml.gz


五、当天的数据转存为e.xml并打包为e.xml.gz,地址：https://epg.136605.xyz/e.xml.gz
