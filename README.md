# 説明
新幹線移動中の通信速度を測定し、Google Earthで可視化するプログラムです


# 使い方


[GPS Logger](https://play.google.com/store/apps/details?id=eu.basicairdata.graziano.gpslogger&hl=ja&pli=1)というAndroidアプリを用いて、GPSのデータをスマホで計測し、ファイルにします

出力として、gpzファイルとkmlファイルが生成されます

新幹線に乗る直前でGPS Loggerを起動して、降りるまで計測を続けてください

GPS計測と同時に、iperfを用いて通信速度計測を行います

iperf計測には、サーバー側とクライアント側の2つが必要です。
サーバー側をAWS等クラウドサービスか、自宅サーバーにセットアップします
クライアント側を、python3とbashが動くPC(macbook等)で動かします

# サーバー側のセットアップ
サーバー側でlinuxを立ち上げます。
ポートの設定で、インバウンドポート5201を開けてください

sshでサーバに入り、
このリポジトリをクローンします
iperf3が使えるように、インストールします

例：
```
sudo apt install iperf3
```

新幹線の移動中はモバイル回線が頻繁に切断され、sshが切断されるため
screenやtmuxを起動し、sshが切れてもプログラムが実行し続けられるようにします。

```
screen
```

その中で下記のコマンドを実行します

```
loop_iperf_server.sh
```

# クライアント側のセットアップ
iperf3が実行できる環境で下記を実行します

```
bash loop_iperf_client.sh xxx.xxx.xxx.xxx(サーバーのipアドレス)
```

上記のコマンドを実行すると、iperf計測が開始されます
新幹線に乗る直前、直後にPCをモバイル回線やテザリングでインターネットに接続してから
実行してください。

# 計測後
新幹線を降りる前か直後に、クライアント側の loop_iperf_client.shを停止してください
サーバー側も出来れば停止しておきます

サーバー側に、
log_shinkansen.csv
というファイルが生成されます。

時刻とスループット、ジッターのデータがcsv形式で保存されています
```
2024-06-10T01:02:02Z, 9535, 1125
2024-06-10T01:02:12Z, 14927, 694
2024-06-10T01:02:22Z, 12179, 1587
2024-06-10T01:02:32Z, 16231, 908
2024-06-10T01:02:42Z, 15094, 1878
2024-06-10T01:02:52Z, 14163, 908
2024-06-10T01:03:02Z, 14723, 458
2024-06-10T01:03:12Z, 16594, 1034
2024-06-10T01:03:22Z, 7700, 5432
2024-06-10T01:03:32Z, 3883, 4226
2024-06-10T01:03:42Z, 7319, 1676
```

また、GPSLoggerも計測を終了します
拡張子がgpx, kmlのファイルが生成されます。
このファイルをPCに移動させておきます

# 可視化
2種類の可視化があります。

## 実速度の可視化
物理的な速度を可視化します。
visualize/velocityディレクトリに移動して、下記のコマンドを実行します
引数には、GPSLoggerで生成されたgpxファイルを指定してください

```
cd visualize/velocity/
python3 main.py 2024xxxx.gpx
```

output.kmlと言うファイルが生成されます。
これをGoogle Earthで読み込ませます
Google Earthを起動 -> +新規 ->ローカルMLファイルのインポートでoutput.kmlを選択
で読み込ませると、速度が可視化されます
![](velocity_visualize.png)

## 通信速度の可視化
iperfで計測した通信速度を可視化します
引数には、gpxファイル、iperfのcsvのパスを指定してください

```
cd visualize/iperf/
python3 main.py 2024xxxx.gpx log_shinkansen.csv
```

output.kmlと言うファイルが生成されます。
これをGoogle Earthで読み込ませます
Google Earthを起動 -> +新規 ->ローカルMLファイルのインポートでoutput.kmlを選択
で読み込ませると、速度が可視化されます

![](iperf_visualize.png)
