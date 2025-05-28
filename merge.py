import os
import glob
import xml.etree.ElementTree as ET
from collections import defaultdict

def extract_date(filename):
    """从文件名中提取日期"""
    try:
        basename = os.path.basename(filename)
        date_str = basename.split("_")[1].split(".")[0]  # 提取 YYYYMMDD
        return int(date_str)
    except Exception:
        return float('inf')  # 发生异常时，放到列表后面

def merge_epg_files(output_file="all.xml"):
    epg_files = sorted(glob.glob("epg_*.xml"), key=extract_date)

    if not epg_files:
        print("没有找到以 epg_ 开头的 XML 文件")
        return

    all_channels = {}
    channel_programmes = defaultdict(list)  # 新增：按 channel_id 分类存储 programme

    for idx, file in enumerate(epg_files):
        print(f"处理文件: {file}")
        try:
            tree = ET.parse(file)
            root = tree.getroot()
        except Exception as e:
            print(f"解析文件 {file} 出错: {e}")
            continue

        # 收集 channel 节点
        for channel in root.findall("channel"):
            channel_id = channel.get("id")
            if channel_id not in all_channels:
                all_channels[channel_id] = channel

        # 收集 programme 节点，并按 channel_id 分类
        for programme in root.findall("programme"):
            channel_id = programme.get("channel")
            if channel_id:
                channel_programmes[channel_id].append(programme)

        print(f"文件 {file} 中已添加 {len(root.findall('programme'))} 个 programme 节点")

    # 创建新的根节点 <tv>
    merged_root = ET.Element("tv")

    # 添加 channel 节点和programme 节点
    for channel_id in all_channels:
        merged_root.append(all_channels[channel_id])
        for programme in channel_programmes[channel_id]:
            merged_root.append(programme)

    # 写入输出文件
    merged_tree = ET.ElementTree(merged_root)
    merged_tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"合并完成，输出文件: {output_file}")

if __name__ == "__main__":
    merge_epg_files()
