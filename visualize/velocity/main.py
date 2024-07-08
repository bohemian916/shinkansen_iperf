import os
import sys

# 指定されたパスを絶対パスに変換
gpx_path = os.path.abspath('../../utils')

# sys.pathにパスを追加
sys.path.append(gpx_path)
import gpx 
import colorbar

import xml.etree.ElementTree as ET
import xml.dom.minidom as md

file_path = sys.argv[1]

# GPXファイルを読み込み、トラックポイントを抽出
gpx_data = gpx.read_gpx(file_path)

trkpts = gpx.extract_trkpts(gpx_data)

# 各ポイント間の時速を計算して表示
speeds = gpx.calculate_speeds(trkpts)

# 最高速度を求める
max_speed = 0
for speed in speeds:
    if speed[4] > max_speed:
        max_speed = speed[4]

print("max speed is " + str(max_speed) + "km/h")
# kml生成
ET.register_namespace('', "http://www.opengis.net/kml/2.2")

tree = ET.parse('templete.xml')
#一番上の階層の要素を取り出します
root = tree.getroot()

print(root.tag)

num=int(max_speed)
diff= 1/num

for document in root.findall('{http://www.opengis.net/kml/2.2}Document'):
    for i in range(num):
        style_element = ET.Element('Style', id='Style' + str(i))
        style_element.text = 'This is a new element.'
        line_style_element = ET.SubElement(style_element, 'LineStyle')
        color_element = ET.SubElement(line_style_element, 'color')
        color_rgb = colorbar.colorBarRGB(i*diff,0.2,0.7)
        color_element.text = 'ff'+ hex(int(color_rgb[2]))[2:].zfill(2) + hex(int(color_rgb[1]))[2:].zfill(2) +hex(int(color_rgb[0]))[2:].zfill(2)
        width_element = ET.SubElement(line_style_element, 'width')
        width_element.text = '5'

        document.append(style_element)

# color bar
        Placemark_element = ET.Element('Placemark', id='p'+str(i))
        name_element = ET.SubElement(Placemark_element, 'name')
        name_element.text = 'sample'
        styleUrl_element = ET.SubElement(Placemark_element, 'styleUrl')
        styleUrl_element.text = '#Style'+str(i)
        description_element = ET.SubElement(Placemark_element, 'description')
        description_element.text = str(i) +"km/h"
        LineString_element = ET.SubElement(Placemark_element, 'LineString')
        extrude_element = ET.SubElement(LineString_element, 'extrude')
        extrude_element.text = '0'
        tessellate_element = ET.SubElement(LineString_element, 'tessellate')
        tessellate_element.text = '0'
        altitudeMode_element = ET.SubElement(LineString_element, 'altitudeMode')
        altitudeMode_element.text = 'clampToGround'
        coordinates_element = ET.SubElement(LineString_element, 'coordinates')

        lat_start = 136.4
        lng_start = 35.50
        coord_text = '\n'
        coord_text = coord_text + "{},{},100\n".format(lat_start+i*0.01, lng_start )
        coord_text = coord_text + "{},{},100\n".format(lat_start+(i+1)*0.01, lng_start)
        coordinates_element.text = coord_text
        document.append(Placemark_element)
# gps speed

    for i,speed in enumerate(speeds):
        if i==0:
            continue

        Placemark_element = ET.Element('Placemark', id='p'+str(i))
        name_element = ET.SubElement(Placemark_element, 'name')
        name_element.text = 'sample'
        description_element = ET.SubElement(Placemark_element, 'description')
        description_element.text = str(speed[4]) +"km/h"
        styleUrl_element = ET.SubElement(Placemark_element, 'styleUrl')
        styleUrl_element.text = '#Style'+str(int(speed[4]))
        LineString_element = ET.SubElement(Placemark_element, 'LineString')
        extrude_element = ET.SubElement(LineString_element, 'extrude')
        extrude_element.text = '0'
        tessellate_element = ET.SubElement(LineString_element, 'tessellate')
        tessellate_element.text = '0'
        altitudeMode_element = ET.SubElement(LineString_element, 'altitudeMode')
        altitudeMode_element.text = 'clampToGround'
        coordinates_element = ET.SubElement(LineString_element, 'coordinates')

        coord_text = '\n'
        coord_text = coord_text + "{},{},100\n".format(speeds[i-1][1], speeds[i-1][0] )
        coord_text = coord_text + "{},{},100\n".format(speeds[i][1], speeds[i][0])
        coordinates_element.text = coord_text
        document.append(Placemark_element)
# 文字列パースを介してminidomへ移す
document = md.parseString(ET.tostring(root, 'utf-8'))

file = open('output.kml', 'w')
# エンコーディング、改行、全体のインデント、子要素の追加インデントを設定しつつファイルへ書き出し
document.writexml(file, encoding='utf-8', newl='\n', indent='', addindent='  ')
#document.writexml(file, encoding='utf-8', newl='', indent='', addindent='  ')
file.close()
