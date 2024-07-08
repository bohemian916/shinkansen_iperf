import os
import sys
from datetime import datetime, timedelta
import csv
import xml.etree.ElementTree as ET
import xml.dom.minidom as md

# 指定されたパスを絶対パスに変換
gpx_path = os.path.abspath('../../utils')

# sys.pathにパスを追加
sys.path.append(gpx_path)
import gpx 


def speed2Style(speed):
    if speed==0:
        return 'Style0' 
    elif speed < 50:
        return 'Style1'
    elif speed < 100:
        return 'Style2'
    elif speed < 500:
        return 'Style3'
    elif speed < 1000:
        return 'Style4'
    elif speed < 5000:
        return 'Style5'
    else : 
        return 'Style6'

style_rgb = {}
style_rgb['Style0'] = (0,0,0) 
style_rgb['Style1'] = (0,0,255) 
style_rgb['Style2'] = (0,127,255) 
style_rgb['Style3'] = (0,127,127) 
style_rgb['Style4'] = (255,255,0) 
style_rgb['Style5'] = (255,127,0) 
style_rgb['Style6'] = (255,0,0) 

style_description = {}
style_description['Style0'] = '0kbps' 
style_description['Style1'] = '1~50kbps' 
style_description['Style2'] = '50~100kbps' 
style_description['Style3'] = '100~500kbps' 
style_description['Style4'] = '500~1000kbps' 
style_description['Style5'] = '1~5Mbps' 
style_description['Style6'] = '5Mbps以上' 

if len(sys.argv) <= 2:
    print("引数に、gpxファイルとiperf_log.csvを指定してください")
    print("usage: python3 main.py test.gpx log.csv")

gpx_file = sys.argv[1]
csv_file = sys.argv[2]

# GPXファイルを読み込み、トラックポイントを抽出
gpx_data = gpx.read_gpx(gpx_file)

trkpts = gpx.extract_trkpts(gpx_data)
interpolited = gpx.interpolate_missing_data(trkpts)

# 時刻データで緯度経度を引ける辞書を作成
gps_date={}
for gps in interpolited:
    dt = gps[3]
    dt_text = '{}Z'.format(dt.strftime('%Y-%m-%dT%H:%M:%S'))
    gps_date[dt_text] = (gps[0], gps[1], gps[2]) 

iperf_data=[]
with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        iperf_data.append((row[0], int(row[1]), int(row[2]))) 

max_speed = 0
for iperf in iperf_data:
    if int(iperf[1]) > max_speed:
        max_speed = int(iperf[1])

# kml生成
ET.register_namespace('', "http://www.opengis.net/kml/2.2")

tree = ET.parse('templete.xml')
#一番上の階層の要素を取り出します
root = tree.getroot()

print(root.tag)

num=int(max_speed)
diff= 1/num

for document in root.findall('{http://www.opengis.net/kml/2.2}Document'):
    for i,style in enumerate(style_rgb):
        style_element = ET.Element('Style', id=style)
        style_element.text = 'This is a new element.'
        line_style_element = ET.SubElement(style_element, 'LineStyle')
        color_element = ET.SubElement(line_style_element, 'color')
        color_element.text = 'ff'+ hex(int(style_rgb[style][2]))[2:].zfill(2) + hex(int(style_rgb[style][1]))[2:].zfill(2) +hex(int(style_rgb[style][0]))[2:].zfill(2)
        width_element = ET.SubElement(line_style_element, 'width')
        width_element.text = '8'

        document.append(style_element)

# color bar
        Placemark_element = ET.Element('Placemark', id='p'+str(i))
        name_element = ET.SubElement(Placemark_element, 'name')
        name_element.text = 'sample'
        description_element = ET.SubElement(Placemark_element, 'description')
        description_element.text = style_description[style] 
        styleUrl_element = ET.SubElement(Placemark_element, 'styleUrl')
        styleUrl_element.text = '#Style'+str(i)
        LineString_element = ET.SubElement(Placemark_element, 'LineString')
        extrude_element = ET.SubElement(LineString_element, 'extrude')
        extrude_element.text = '0'
        tessellate_element = ET.SubElement(LineString_element, 'tessellate')
        tessellate_element.text = '0'
        altitudeMode_element = ET.SubElement(LineString_element, 'altitudeMode')
        altitudeMode_element.text = 'clampToGround'
        coordinates_element = ET.SubElement(LineString_element, 'coordinates')

        lat_start = 137.0
        lng_start = 36.00
        coord_text = '\n'
        coord_text = coord_text + "{},{},100\n".format(lat_start+i*0.3, lng_start )
        coord_text = coord_text + "{},{},100\n".format(lat_start+(i+1)*0.3, lng_start)
        coordinates_element.text = coord_text
        document.append(Placemark_element)

# iperf speed

    for i,iperf in enumerate(iperf_data):
        if i==0:
            continue

        speed = iperf[1] 
        dt = iperf[0]
        lat = gps_date[dt][0] 
        lon = gps_date[dt][1] 
        alt = gps_date[dt][2] 

        dt_obj = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")
        # 1秒前のdatetimeオブジェクトを計算
        pre_dt_obj = dt_obj - timedelta(seconds=10)
        # datetimeオブジェクトを指定の形式の文字列に変換
        pre_dt = pre_dt_obj.strftime("%Y-%m-%dT%H:%M:%SZ")

        pre_lat = gps_date[pre_dt][0]
        pre_lon = gps_date[pre_dt][1]
        pre_alt = gps_date[pre_dt][2]

        Placemark_element = ET.Element('Placemark', id='p'+str(i))
        name_element = ET.SubElement(Placemark_element, 'name')
        name_element.text = 'sample'
        description_element = ET.SubElement(Placemark_element, 'description')
        description_element.text = str(speed)+ 'kbps' 
        styleUrl_element = ET.SubElement(Placemark_element, 'styleUrl')
        styleUrl_element.text = '#'+speed2Style(int(speed))
        LineString_element = ET.SubElement(Placemark_element, 'LineString')
        extrude_element = ET.SubElement(LineString_element, 'extrude')
        extrude_element.text = '0'
        tessellate_element = ET.SubElement(LineString_element, 'tessellate')
        tessellate_element.text = '0'
        altitudeMode_element = ET.SubElement(LineString_element, 'altitudeMode')
        altitudeMode_element.text = 'clampToGround'
        coordinates_element = ET.SubElement(LineString_element, 'coordinates')

        coord_text = '\n'
        coord_text = coord_text + "{},{},{}\n".format(lon, lat,alt+200)
        coord_text = coord_text + "{},{},{}\n".format(pre_lon, pre_lat, pre_alt+200)
        coordinates_element.text = coord_text
        document.append(Placemark_element)
# 文字列パースを介してminidomへ移す
document = md.parseString(ET.tostring(root, 'utf-8'))

file = open('output.kml', 'w')
# エンコーディング、改行、全体のインデント、子要素の追加インデントを設定しつつファイルへ書き出し
document.writexml(file, encoding='utf-8', newl='\n', indent='', addindent='  ')
#document.writexml(file, encoding='utf-8', newl='', indent='', addindent='  ')
file.close()
