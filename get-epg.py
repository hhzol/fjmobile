import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import xml.dom.minidom

#数据接口的部分url含固定参数
fixurl = "http://watchtv.fja.bcs.ottcn.com:8080/cms-lvp-epg/lvps/getAllProgramlist?abilityString=%257B%2522CITY_CODE%2522%253A%2522592%2522%252C%2522COUNTY_CODE%2522%253A%2522201%2522%252C%2522VILLAGE_CODE%2522%253A%2522000102091010000414404459%2522%252C%2522abilities%2522%253A%255B%2522Playable-YOUKU%257CPlayable-IQIYI%257CDL-3rd%2522%252C%25224K-1%257CtimeShift%257CNxM%2522%252C%25224K-1%257Ccp-TENCENT%2522%255D%252C%2522businessGroupIds%2522%253A%255B%255D%252C%2522deviceGroupIds%2522%253A%255B%25222081%2522%255D%252C%2522districtCode%2522%253A%2522350200%2522%252C%2522labelIds%2522%253A%255B%25223570%2522%255D%252C%2522userGroupIds%2522%253A%255B%2522350000%2522%255D%252C%2522userLabelIds%2522%253A%255B%25223570%2522%255D%257D"

# 获取数据的起止日期：今明后三天
base_date0 = datetime.today().date()
startdate = (base_date0  - timedelta(days=0)).strftime("%Y%m%d")
enddate = (base_date0  + timedelta(days=2)).strftime("%Y%m%d")

# 从channels.txt中读取频道uuid
channels = {}
with open('channels.txt', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, start=1):
        line = line.strip()
        if not line or '|' not in line:
            continue
        name, uuid = line.split('|', 1)
        url = f"{fixurl}&startDate={startdate}&endDate={enddate}&pos=fullplayer&uuid={uuid}"
        channels[str(idx)] = {'channel_name': name, 'url': url}

# 获取每个频道的所有数据（只访问一次接口）
channel_data = {}
for channel_id, info in channels.items():
    response = requests.get(info['url'])
    data = response.json()
    channel_data[channel_id] = data.get('content', [])
    print(f"已获取频道: {info['channel_name']}")

# 获取今天时间，以确定生成的xml日期
tz = timezone(timedelta(hours=8))
base_date = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)

# 按日期生成XML
for offset in range(2):  # 1=明天, 2=后天
    appoint_date = base_date + timedelta(days=(offset+1))
    target_playDate = int(appoint_date.timestamp())
    date_str = appoint_date.strftime('%Y%m%d')

    tv = ET.Element('tv')

    # 添加channel节点
    for channel_id, info in channels.items():
        channel_element = ET.SubElement(tv, 'channel', id=channel_id)
        display_name = ET.SubElement(channel_element, 'display-name')
        display_name.text = info['channel_name']

    # 按频道顺序添加programme节点
    for channel_id, programs_by_day in channel_data.items():
        programs = []
        for day in programs_by_day:
            if day.get('playDate') == target_playDate:
                programs.extend(day.get('programs', []))

        programs.sort(key=lambda x: x['startTime'])
        next_start_dt = None

        for program in programs:
            start_dt = datetime.fromtimestamp(program['startTime'], tz)
            end_dt = datetime.fromtimestamp(program['endTime'], tz)

            if next_start_dt and start_dt > next_start_dt:
                prog0 = ET.SubElement(tv, "programme", {
                    "start": next_start_dt.strftime("%Y%m%d%H%M%S") + " +0800",
                    "stop": start_dt.strftime("%Y%m%d%H%M%S") + " +0800",
                    "channel": channel_id
                })
                title0 = ET.SubElement(prog0, "title")
                title0.text = "**（隐藏的节目名）**"

            if start_dt.date() != end_dt.date() and (end_dt.hour != 0 or end_dt.minute != 0):
                part1_stop = datetime.combine(start_dt.date(), datetime.max.time(), tz)
                part1_stop = part1_stop.replace(hour=23, minute=59, second=59)
                prog1 = ET.SubElement(tv, "programme", {
                    "start": start_dt.strftime("%Y%m%d%H%M%S") + " +0800",
                    "stop": part1_stop.strftime("%Y%m%d%H%M%S") + " +0800",
                    "channel": channel_id
                })
                title1 = ET.SubElement(prog1, "title")
                title1.text = program['programName']

                part2_start = datetime.combine(end_dt.date(), datetime.min.time(), tz)
                prog2 = ET.SubElement(tv, "programme", {
                    "start": part2_start.strftime("%Y%m%d%H%M%S") + " +0800",
                    "stop": end_dt.strftime("%Y%m%d%H%M%S") + " +0800",
                    "channel": channel_id
                })
                title2 = ET.SubElement(prog2, "title")
                title2.text = program['programName']
            else:
                prog = ET.SubElement(tv, "programme", {
                    "start": start_dt.strftime("%Y%m%d%H%M%S") + " +0800",
                    "stop": end_dt.strftime("%Y%m%d%H%M%S") + " +0800",
                    "channel": channel_id
                })
                title = ET.SubElement(prog, "title")
                title.text = program['programName']

            next_start_dt = end_dt

    # 保存XML文件
    xml_string = ET.tostring(tv, encoding='utf-8')
    dom = xml.dom.minidom.parseString(xml_string)
    pretty_xml = dom.toprettyxml(indent="  ")
    with open(f'epg_{date_str}.xml', 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    print(f"生成文件: epg_{date_str}.xml 完成！")
