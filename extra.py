import xml.etree.ElementTree as ET
from collections import defaultdict

def load_include_names(filename):
    """从文件中读取需要保留的频道名称"""
    include = set()
    try:
        with open(filename, encoding='utf-8') as f:
            for line in f:
                name = line.strip()
                if name:
                    include.add(name)
    except FileNotFoundError:
        print(f"⚠️ 警告: 文件 {filename} 不存在，将不使用频道筛选！")
    return include

def merge_epg_restructured(e_file, e1_file, output_file, include_file):
    include_names = load_include_names(include_file)

    # 解析 XML 文件
    tree_e = ET.parse(e_file)
    root_e = tree_e.getroot()

    tree_e1 = ET.parse(e1_file)
    root_e1 = tree_e1.getroot()

    # 提取 e.xml 的频道名和 id
    e_channels = {ch.find('display-name').text.strip(): ch.get('id') for ch in root_e.findall('channel')}
    e_channel_ids = set(e_channels.values())
    max_channel_id = max((int(cid) for cid in e_channel_ids if cid.isdigit()), default=0)

    # 存储频道和节目
    channel_id_mapping = {}
    channels_dict = {}
    programme_dict = defaultdict(list)

    # 先添加 e.xml 的频道
    for channel in root_e.findall('channel'):
        cid = channel.get('id')
        channels_dict[cid] = channel

    # 处理 e1.xml 中需要保留的频道（不在 e.xml 中的）
    for channel in root_e1.findall('channel'):
        display_name = channel.find('display-name').text.strip()
        old_id = channel.get('id')
        if display_name not in e_channels and display_name in include_names:
            max_channel_id += 1
            new_id = str(max_channel_id)
            channel.set('id', new_id)
            channels_dict[new_id] = channel
            channel_id_mapping[old_id] = new_id  # 旧id到新id的映射

    # 收集 e.xml 节目
    for programme in root_e.findall('programme'):
        channel_id = programme.get('channel')
        programme_dict[channel_id].append(programme)

    # 收集 e1.xml 节目并更新 channel id
    for programme in root_e1.findall('programme'):
        old_channel_id = programme.get('channel')
        new_channel_id = channel_id_mapping.get(old_channel_id)
        if new_channel_id:
            programme.set('channel', new_channel_id)
            programme_dict[new_channel_id].append(programme)

    # 构建新 XML 树
    merged_root = ET.Element('tv')
    for channel_id, channel in channels_dict.items():
        merged_root.append(channel)
        for programme in sorted(programme_dict[channel_id], key=lambda p: p.get('start')):
            merged_root.append(programme)

    # 输出 XML
    xml_string = ET.tostring(merged_root, encoding='utf-8', xml_declaration=True)
    with open(output_file, 'wb') as f:
        f.write(xml_string)

    print(f"✅ 合并完成！生成文件：{output_file}")

if __name__ == "__main__":
    e_file = "all.xml"
    e1_file = "sources.xml"
    output_file = "more.xml"
    include_file = "extra_channels.txt"
    merge_epg_restructured(e_file, e1_file, output_file, include_file)
