import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import xml.dom.minidom

fixurl = "http://watchtv.fja.bcs.ottcn.com:8080/cms-lvp-epg/lvps/getAllProgramlist?abilityString=%257B%2522CITY_CODE%2522%253A%2522592%2522%252C%2522COUNTY_CODE%2522%253A%2522201%2522%252C%2522VILLAGE_CODE%2522%253A%2522000102091010000414404459%2522%252C%2522abilities%2522%253A%255B%2522Playable-YOUKU%257CPlayable-IQIYI%257CDL-3rd%2522%252C%25224K-1%257CtimeShift%257CNxM%2522%252C%25224K-1%257Ccp-TENCENT%2522%255D%252C%2522businessGroupIds%2522%253A%255B%255D%252C%2522deviceGroupIds%2522%253A%255B%25222081%2522%255D%252C%2522districtCode%2522%253A%2522350200%2522%252C%2522labelIds%2522%253A%255B%25223570%2522%255D%252C%2522userGroupIds%2522%253A%255B%2522350000%2522%255D%252C%2522userLabelIds%2522%253A%255B%25223570%2522%255D%257D"

# 各频道对应 uuid
channel_uuids = {
    "CCTV1": "HD-8000k-1080P-lowcctv1",
    "CCTV2": "cctv-2",
    "CCTV3": "HD-8M-1080P-cctv3",
    "CCTV4": "cctv-4",
    "CCTV5": "HD-8M-1080P-cctv5",
    "CCTV5+": "HD-8000k-1080P-cctv05plus",
    "CCTV6": "HD-8M-1080P-cctv6",
    "CCTV7": "HD-8000k-1080P-cctv7",
    "CCTV8": "HD-8M-1080P-cctv8",
    "CCTV9": "HD-8000k-1080P-cctv9",
    "CCTV10": "HD-8000k-1080P-cctv10",
    "CCTV11": "cctv-11",
    "CCTV12": "HD-8000k-1080P-cctv12",
    "CCTV13": "cctv-13",
    "CCTV14": "HD-8000k-1080P-cctv14",
    "CCTV15": "cctv-15",
    "CCTV16": "HD-8000k-1080P-cctv16",
    "CCTV16 4K": "HD-20M-2160P-cctv16",
    "CCTV17": "HD-8000k-1080P-cctv17",
    "CGTN纪录": "cctv-9",
    "CGTN": "cctv19",
    "CGTN法语": "SD-4000k-576P-CGTNFrench",
    "CGTN俄语": "SD-4000k-576P-CGTNRussia",
    "CGTN西语": "SD-4000k-576P-CGTNEspana",
    "CGTN阿语": "SD-4000k-576P-CGTNArab",
    "中国天气": "fjzgqixiang",
    "CETV1": "jiaoyutv",
    "CETV2": "fjjiaoyutv2",
    "CETV4": "SD-4000k-576P-jiaoyutv4",
    "福建综合": "fjzonghe",
    "东南卫视": "fjdongnanstv",
    "福建乡村振兴": "fjxiangcunzxgg",
    "福建新闻": "fjxinwen",
    "福建电视剧": "fjdianshiju",
    "福建旅游": "fjlvyou",
    "福建经济": "fjjingjish",
    "福建文体": "fjtiyu",
    "福建少儿": "fjshaoer",
    "海峡卫视": "fjhaixia",
    "福建教育": "fjjiaoyu",
    "厦门卫视": "HD-4000k-1080P-xiamenstv",
    "厦门1": "HD-4000k-1080P-xiamen1",
    "厦门2": "HD-4000k-1080P-xiamen2",
    "厦门3": "HD-4000k-1080P-xiamen3",
    "北京卫视": "fjbeijingstv",
    "天津卫视": "fjtianjinstv",
    "河北卫视": "HD-8000k-1080P-bsthebeistv",
    "山西卫视": "fjshanxistv",
    "内蒙古卫视": "fjneimenggustv",
    "辽宁卫视": "HD-8000k-1080P-bstliaoningstv",
    "吉林卫视": "jilin1",
    "黑龙江卫视": "fjheilongjiangstv",
    "东方卫视": "HD-8000k-1080P-bstdongfangstv",
    "江苏卫视": "HD-8000k-1080P-bstjiangsustv",
    "浙江卫视": "fjzhejiangstv",
    "安徽卫视": "HD-8000k-1080P-bstanhuistv",
    "江西卫视": "fjjiangxistv",
    "山东卫视": "fjshandongstv",
    "河南卫视": "henanstv",
    "湖北卫视": "fjhubeistv",
    "湖南卫视": "fjhunanstv",
    "广东卫视": "HD-8000k-1080P-bstguangdongstv",
    "广西卫视": "fjguangxistv",
    "海南卫视": "lvyoustv",
    "重视卫视": "fjchongqingstv",
    "四川卫视": "HD-8000k-1080P-bstsichuanstv",
    "贵州卫视": "fjguizhoustv",
    "云南卫视": "yntv1",
    "西藏卫视": "fjxizangstv",
    "陕西卫视": "fjshanxi1stv",
    "甘肃卫视": "fjgansustv",
    "青海卫视": "fjqinghaistv",
    "宁夏卫视": "fjnignxiastv",
    "新疆卫视": "fjxinjiangstv",
    "深圳卫视": "fjshenzhenstv",
    "兵团卫视": "SD-2500k-576P-bstbingtuanstv",
    "三沙卫视": "HD-2500k-1080P-bstsanshastv",
    "康巴卫视": "kamba-tv",
    "延边卫视": "SD-4000k-576P-yanbianstv",
    "纪实科教": "HD-8000k-1080P-beijingjishi",
    "先锋乒羽": "SD-2000k-576P-xianfengpy",
    "快乐垂钓": "HD-2000k-1080P-happyfishing",
    "山东教育": "shandongjy",
    "茶频道": "SD-2000k-576P-chapd",
    "金鹰纪实": "HD-8000k-1080P-mgjinyingjishi",
    "金鹰卡通": "SD-8000k-1080P-yingyinkaton",
    "哈哈炫动": "xuandongkaton",
    "卡酷少儿": "kakukaton",
    "嘉佳卡通": "fjjiajiakatong",
    "优漫卡通": "youmankaton",
    "精品大剧": "jdaju",
    "古装剧场": "guzhuangjc",
    "军旅剧场": "junlvjc",
    "家庭剧场": "jiatingjc",
    "热播精选": "xiqumd",
    "爱情喜剧": "aiqingxj",
    "动作电影": "dongzuody",
    "精品综合": "mingxingdp",
    "惊悚悬疑": "jingsongxy",
    "黑莓电影": "HD-8000k-1080P-Supermovie",
    "金牌综艺": "saishijx",
    "精品体育": "jtiyu",
    "精品萌宠": "jingpinmc",
    "中国功夫": "SD-1500k-576P-gzkongfu",
    "黑莓动画": "HD-8000k-1080P-Supercctv14",
    "怡伴健康": "ljiankangyouyue",
    "潮妈辣婆": "HD-1500k-720P-cmlapo",
    "哒啵赛事": "HD-8000k-1080P-Superwmyx",
    "哒啵电竞": "dabodj",
    "精品纪录": "jingpinjl",
    "军事评论": "junshipl",
    "炫舞未来": "HD-4000k-1080P-xwwl",
    "CCTV4K": "HD-15M-2160P-cctv4k",
    "北京卫视4K": "FJGD-SMS-beijingstv4k",
    "纯享4K": "HD-20M-2160P-chunxiang4k",
    "睛彩青少": "HD-8000k-1080P-quanminrl",
    "睛彩竞技": "HD-8000k-1080P-miguaoyun2",
    "睛彩篮球": "HD-8000k-1080P-miguaoyun1",
    "睛彩广场舞": "MIGU-8000k-1080P-jcgcw"
}

# 获取今天日期
today = datetime.today().date()
startdate = (today + timedelta(days=0)).strftime("%Y%m%d")
enddate = (today + timedelta(days=6)).strftime("%Y%m%d")

# 生成完整频道地址
channels = {}
for name, uuid in channel_uuids.items():
    full_url = f"{fixurl}&startDate={startdate}&endDate={enddate}&pos=fullplayer&uuid={uuid}"
    channels[name] = full_url

# 创建TV根节点
tv = ET.Element('tv')

# 添加channel节点
for channel_name in channels:
    channel_element = ET.SubElement(tv, 'channel', id=channel_name)
    display_name = ET.SubElement(channel_element, 'display-name')
    display_name.text = channel_name

# 定义今天5:00AM时间点
today_5am = datetime.combine(today, datetime.min.time()) + timedelta(hours=5)

# 处理每个频道的节目单
for channel_name, url in channels.items():
    response = requests.get(url)
    data = response.json()

    # 收集所有节目
    programs = []
    for day in data.get('content', []):
        for program in day.get('programs', []):
            programs.append(program)

    # 按时间升序排序
    programs.sort(key=lambda x: x['startTime'])
    next_start_dt= None
    for program in programs:
        start_timestamp = program['startTime']
        end_timestamp = program['endTime']
        start_dt = datetime.fromtimestamp(start_timestamp)
        end_dt = datetime.fromtimestamp(end_timestamp)

        # 跳过5:00AM之前的节目
        if start_dt < today_5am:
            continue

        if next_start_dt is not None and start_dt > next_start_dt:
            prog0 = ET.SubElement(tv, "programme", {
                "start": next_start_dt.strftime("%Y%m%d%H%M%S") + " +0800",
                "stop": start_dt.strftime("%Y%m%d%H%M%S") + " +0800",
                "channel": channel_name
            })
            title0 = ET.SubElement(prog0, "title")
            title0.text = "**（隐藏的节目名）**"
        if start_dt.date() != end_dt.date() and (end_dt.hour != 0 or end_dt.minute != 0):
            # 分拆跨天的节目
            # 第一段
            part1_stop = datetime.combine(start_dt.date(), datetime.max.time()).replace(hour=23, minute=59, second=59)
            prog1 = ET.SubElement(tv, "programme", {
                "start": start_dt.strftime("%Y%m%d%H%M%S") + " +0800",
                "stop": part1_stop.strftime("%Y%m%d%H%M%S") + " +0800",
                "channel": channel_name
            })
            title1 = ET.SubElement(prog1, "title")
            title1.text = program['programName']
            # 第二段
            part2_start = datetime.combine(end_dt.date(), datetime.min.time())
            prog2 = ET.SubElement(tv, "programme", {
                "start": part2_start.strftime("%Y%m%d%H%M%S") + " +0800",
                "stop": end_dt.strftime("%Y%m%d%H%M%S") + " +0800",
                "channel": channel_name
            })
            title2 = ET.SubElement(prog2, "title")
            title2.text = program['programName']
        else:
            programme = ET.SubElement(tv, "programme", {
                "start": start_dt.strftime("%Y%m%d%H%M%S") + " +0800",
                "stop": end_dt.strftime("%Y%m%d%H%M%S") + " +0800",
                "channel": channel_name
            })
            title = ET.SubElement(programme, "title")
            title.text = program['programName']
        next_start_dt=end_dt

# 格式化输出XML
xml_string = ET.tostring(tv, encoding='utf-8')
dom = xml.dom.minidom.parseString(xml_string)
pretty_xml = dom.toprettyxml(indent="  ")

# 输出结果
with open('fj.xml', 'w', encoding='utf-8') as f:
    f.write(pretty_xml)

print('XMLTV文件已生成完毕！')
