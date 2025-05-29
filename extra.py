import xml.etree.ElementTree as ET
from xml.dom import minidom

def clean_pretty_xml(xml_string):
    reparsed = minidom.parseString(xml_string)
    for node in reparsed.childNodes:
        if node.nodeType == node.TEXT_NODE:
            continue
        clean_node(node)
    return reparsed.toprettyxml(indent="  ", encoding="utf-8")

def clean_node(node):
    remove_list = []
    for child in node.childNodes:
        if child.nodeType == child.TEXT_NODE and child.data.strip() == "":
            remove_list.append(child)
        elif child.hasChildNodes():
            clean_node(child)
    for child in remove_list:
        node.removeChild(child)

def merge_epg_restructured(e_file, e1_file, output_file):
    # 需要删除的频道名称
    excluded_names = {"北京纪实科教", "厦门综合", "厦门海峡", "noepg"}

    # 解析 e.xml
    tree_e = ET.parse(e_file)
    root_e = tree_e.getroot()

    # 解析 e1.xml
    tree_e1 = ET.parse(e1_file)
    root_e1 = tree_e1.getroot()

    # 收集 e.xml 中的频道名
    e_channel_names = {ch.find('display-name').text.strip() for ch in root_e.findall('channel')}
    e_channel_ids = {ch.get('id') for ch in root_e.findall('channel')}
    max_channel_id = max(int(cid) for cid in e_channel_ids if cid.isdigit())

    # 频道名映射
    channel_id_mapping = {}

    # 收集 e1 中需要保留的频道和节目
    new_channels = []
    new_programmes = {}

    for channel in root_e1.findall('channel'):
        display_name = channel.find('display-name').text.strip()
        old_id = channel.get('id')
        if display_name not in e_channel_names and display_name not in excluded_names:
            max_channel_id += 1
            new_id = str(max_channel_id)
            channel.set('id', new_id)
            new_channels.append(channel)
            channel_id_mapping[old_id] = new_id
            new_programmes[new_id] = []

    for programme in root_e1.findall('programme'):
        old_channel_id = programme.get('channel')
        if old_channel_id in channel_id_mapping:
            new_channel_id = channel_id_mapping[old_channel_id]
            programme.set('channel', new_channel_id)
            new_programmes[new_channel_id].append(programme)

    # 创建新的根节点
    merged_root = ET.Element('tv')

    # 添加 e.xml 中的频道和节目
    for channel in root_e.findall('channel'):
        merged_root.append(channel)
        channel_id = channel.get('id')
        for programme in root_e.findall('programme'):
            if programme.get('channel') == channel_id:
                merged_root.append(programme)

    # 添加 e1.xml 中独有的频道和节目
    for channel in new_channels:
        merged_root.append(channel)
        cid = channel.get('id')
        for programme in new_programmes.get(cid, []):
            merged_root.append(programme)

    # 生成字符串
    rough_string = ET.tostring(merged_root, encoding='utf-8')
    pretty_xml = clean_pretty_xml(rough_string)

    # 保存结果
    with open(output_file, 'wb') as f:
        f.write(pretty_xml)

    print(f"✅ 合并完成！生成文件：{output_file}")

if __name__ == "__main__":
    e_file = "all.xml"
    e1_file = "sources.xml"
    output_file = "more.xml"
    merge_epg_restructured(e_file, e1_file, output_file)
