import os
import glob
import xml.etree.ElementTree as ET

def extract_date(filename):
    """从文件名中提取日期"""
    try:
        date_str = filename.split("_")[1].split(".")[0]  # 提取 YYYYMMDD
        return int(date_str)
    except Exception:
        return float('inf')  # 发生异常时，放到列表后面

def merge_epg_files(output_file="all.xml"):
    # 获取当前目录下所有 epg_ 开头的 xml 文件，并按日期排序
    epg_files = sorted(glob.glob("epg_*.xml"), key=extract_date)
    
    if not epg_files:
        print("没有找到以 epg_ 开头的 XML 文件")
        return

    merged_tree = None
    merged_root = None
    all_channels = {}
    all_programmes = []

    for idx, file in enumerate(epg_files):
        print(f"处理文件: {file}")
        tree = ET.parse(file)
        root = tree.getroot()

        if idx == 0:
            # 第一个文件用于保留基础结构
            merged_tree = tree
            merged_root = root

        # 收集 <channel> 节点
        for channel in root.findall("channel"):
            channel_id = channel.get("id")
            if channel_id not in all_channels:
                all_channels[channel_id] = channel

        # 收集 <programme> 节点
        all_programmes.extend(root.findall("programme"))

    # 清空原有 <channel> 和 <programme> 节点
    for elem in merged_root.findall("channel"):
        merged_root.remove(elem)
    for elem in merged_root.findall("programme"):
        merged_root.remove(elem)

    # 添加去重后的 <channel> 节点
    for channel in all_channels.values():
        merged_root.append(channel)

    # 添加所有 <programme> 节点
    for programme in all_programmes:
        merged_root.append(programme)

    # 保存合并后的文件
    merged_tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"合并完成，输出文件: {output_file}")

if __name__ == "__main__":
    merge_epg_files()
