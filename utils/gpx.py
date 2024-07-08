import gpxpy
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta
from typing import List, Tuple

# GPXファイルを読み込む関数
def read_gpx(file_path):
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
    return gpx

# トラックポイントを抽出する関数
def extract_trkpts(gpx):
    trkpts = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                trkpts.append((point.latitude, point.longitude, point.elevation, point.time))
    return trkpts

#補完
def interpolate_missing_data(data: List[Tuple[float, float, float, datetime]]) -> List[Tuple[float, float, float, datetime]]:
    interpolated_data = []
    
    for i in range(len(data) - 1):
        interpolated_data.append(data[i])
        
        current_time = data[i][3]
        next_time = data[i + 1][3]
        diff = (next_time - current_time).seconds
        
        # If the time difference is greater than 1 second, interpolate
        if diff > 1:
            for j in range(1, diff):
                new_time = current_time + timedelta(seconds=j)
                fraction = j / diff
                
                # Linear interpolation for latitude, longitude, and altitude
                new_lat = data[i][0] + fraction * (data[i + 1][0] - data[i][0])
                new_lon = data[i][1] + fraction * (data[i + 1][1] - data[i][1])
                new_alt = data[i][2] + fraction * (data[i + 1][2] - data[i][2])
                
                interpolated_data.append((new_lat, new_lon, new_alt, new_time))
    
    # Add the last data point
    interpolated_data.append(data[-1])
    
    return interpolated_data

# Haversine関数を使って距離を計算
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # 地球の半径 (km)
    
    lat1, lon1 = radians(lat1), radians(lon1)
    lat2, lon2 = radians(lat2), radians(lon2)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return distance

# 速度を計算して表示する関数
def calculate_speeds(trkpts):
    speeds = []
    for i in range(1, len(trkpts)):
        lat1, lon1, elevation1, time1 = trkpts[i - 1]
        lat2, lon2, elevation2, time2 = trkpts[i]
        
        distance = haversine(lat1, lon1, lat2, lon2)  # 距離 (km)
        time_diff = (time2 - time1).total_seconds() / 3600  # 時間の差 (hours)
        
        if time_diff > 0:
            speed = distance / time_diff  # 時速 (km/h)
            speeds.append((lat2, lon2, elevation2, time2,speed))
#            print(f"Point {i}: Speed = {speed:.2f} km/h")
        else:
#            print(f"Point {i}: Time difference is zero, cannot calculate speed.")
            speeds.append((lat2,lon2,elevation2, time2,0))
    return speeds 

# GPXファイルのパスを指定
if __name__ == '__main__':
    import sys
    file_path = sys.argv[1] 

    # GPXファイルを読み込み、トラックポイントを抽出
    gpx = read_gpx(file_path)

    trkpts = extract_trkpts(gpx)

    interpolated_data = interpolate_missing_data(trkpts)
    for d in interpolated_data:
        print(d)


    # 各ポイント間の時速を計算して表示
    #speeds = calculate_speeds(trkpts)
    # 結果を表示
    #for trkpt in trkpts:
    #    print(trkpt)
#    for speed in speeds:
#        print(speed)


