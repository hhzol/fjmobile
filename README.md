一、每日从移动机顶盒接口抓取明天和后天的epg数据,生成两个文件，文件名格式为epg_yyyymmdd.xml


二、将超过9天的数据删除（即7天以前）


三、将9天的历史数据（含明后天）合并为all.xml并打包为all.xml.gz


四、当天的数据转存为e.xml并打包为e.xml.gz


五、频道的准确名称见channels.txt
