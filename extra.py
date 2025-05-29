import xml.etree.ElementTree as ET

# 新增：从文件读取需要保留的频道名
def load_include_names(filename):
    include = set()
    try:
        with open(filename, encoding='utf-8') as f:
            for line in f:
                name = line.strip()
                if name:  # 跳过空行
                    include.add(name)
    except FileNotFoundError:
        print(f"⚠️ 警告: 文件 {filename} 不存在，使用空的排除列表！")
    return include

def merge_epg_restructured(e_file, e1_file, output_file, include_file):
    # 从文件读取需要保留的频道名称
    include_names = load_include_names(include_file)

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

    # 频道 ID 映射表：new_id -> old_id
    channel_id_mapping = {}

    # 创建新的根节点
    merged_root = ET.Element('tv')

    # 添加 e.xml 中的频道和节目
    for channel in root_e.findall('channel'):
        merged_root.append(channel)
    for programme in root_e.findall('programme'):
        merged_root.append(programme)

    # 收集 e1 中需要保留的频道和节目
    new_channels = []
    new_programmes = {}

    for channel in root_e1.findall('channel'):
        display_name = channel.find('display-name').text.strip()
        old_id = channel.get('id')
        if display_name not in e_channel_names and display_name in include_names:
            max_channel_id += 1
            new_id = str(max_channel_id)
            channel.set('id', new_id)
            new_channels.append(channel)
            channel_id_mapping[new_id] = old_id
            new_programmes[new_id] = []

    for programme in root_e1.findall('programme'):
        old_channel_id = programme.get('channel')
        # 检查这个 old_channel_id 是否在映射表里
        for new_id, old_id in channel_id_mapping.items():
            if old_channel_id == old_id:
                # 替换频道 ID
                programme.set('channel', new_id)
                new_programmes[new_id].append(programme)
                break

    # 添加 e1.xml 中独有的频道和节目
    for channel in new_channels:
        merged_root.append(channel)
        cid = channel.get('id')
        for programme in new_programmes.get(cid, []):
            merged_root.append(programme)

    # 保存 xml
    xml_string = ET.tostring(merged_root, encoding='utf-8', xml_declaration=True)
    with open(output_file, 'wb') as f:
        f.write(xml_string)

    print(f"✅ 合并完成！生成文件：{output_file}")

if __name__ == "__main__":
    e_file = "all.xml"
    e1_file = "sources.xml"
    output_file = "more.xml"
    include_file = "extra_channels.txt"  # 需要保留的频道列表
    merge_epg_restructured(e_file, e1_file, output_file, include_file)
