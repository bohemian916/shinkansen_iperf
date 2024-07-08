#!/usr/bin/env python3

import subprocess
import contextlib
import sys, os
import re
from enum import Enum
import datetime

#
# from https://gist.github.com/thelinuxkid/5114777 
####
def unbuffered(proc, stream='stdout'):
    newlines = ['\n', '\r\n', '\r']
    stream = getattr(proc, stream)
    with contextlib.closing(stream):
        while True:
            out = []
            last = stream.read(1)
            if last == '' and proc.poll() is not None:
                break
            while last not in newlines:
                if last == '' and proc.poll() is not None:
                    break
                out.append(last)
                last = stream.read(1)
            out = ''.join(out)
            yield out
####

class iperf_srv:
    class parse_state_kind(Enum):
        begin = 1
        transfer = 2
        end = 3

    def __init__(self, conn_port, interval):
        self.conn_port = conn_port
        self.interval = interval

        self.parse_state = iperf_srv.parse_state_kind.begin

    def stream(self):
        zero_count = 0

        proc = subprocess.Popen([ 
                               "/usr/bin/iperf3",  
                               "-V",
                               "-1",  # one time off
                               "-s",
                               "-p", "{}".format(self.conn_port),
                               "-i", "{}".format(self.interval),
                               "--forceflush",
                               "-f",  "k",    # kilobits
                               ],
                               stdout=subprocess.PIPE,
                               universal_newlines = True,
                               bufsize=1
                               )
        for line in unbuffered(proc):
            exp_data = self.parse(line)

            if exp_data and exp_data.get("throughput") == 0:
                zero_count +=1 
                if zero_count > 1:
                    proc.terminate()
            else:
                zero_count = 0
            yield line.strip()

    def parse(self, line):
        # print('parse status', self.parse_state, line)
        # [ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
        begin_st = r'\[[ ]+ID\][ \t]+Interval[ \t]+Transfer[ \t]+Bitrate[ \t]+Jitter[ \t]+Lost/Total Datagrams$'
        end_st = '^[ -]+'

        res = None

        if self.parse_state == iperf_srv.parse_state_kind.begin:
            if re.search(begin_st, line): 
                self.parse_state = iperf_srv.parse_state_kind.transfer
                print("# start iperf forwarding")
            else:
                pass
        elif  self.parse_state == iperf_srv.parse_state_kind.transfer:
            """[  5]   5.00-5.20   sec  1.29 MBytes  54000    Kbits/sec  0.013   ms         0/1350               (0%)"""
            """  id   bgn   end         trans_sz     bitrate  Kbits/sec  jitter  jit_kind   loss_cnt/total_cnt   rate """

            trans_patt = r'^\[[ ]*(\d+)\][ ]+([\d.]+)-([\d.]+)[ ]+sec[ ]+([\d.]+)[ ]+(\w+)[ ]*([\d.]+)[ ]*Kbits/sec[ ]+([\d.]+)[ ]+(\w+)[ ]+(\d+)/(\d+)[ ]+\((\d+(?:\.\d+)?)%\)'
            m = re.match(trans_patt, line)
            if m:
                stream_id, t_bgn, t_end, trans_sz, trans_kind, bitrate, jitter, jit_kind, loss_cnt, total_cnt, _rate = m.groups()
                stream_id = int(stream_id)
                t_bgn = float(t_bgn)
                t_end = float(t_end)
                if trans_kind == 'KByte':
                    trans_sz = 1024 * float(trans_sz)
                elif trans_kind == 'MByte':
                    trans_sz = (1024*1024) * float(trans_sz)
                elif trans_kind == 'GByte':
                    trans_sz = (1024*1024*1024) * float(trans_sz)
                else:
                    trans_sz = float(trans_sz)

                jitter = float(jitter)
                if jit_kind == 'ms':
                    jitter = jitter * 1e3
                elif jit_kind == 'sec' or jit_kind == 's':
                    jitter = jitter * 1e6
                else:
                    print('Error: jitter kind ')
                    assert(0)

                bitrate = round(float(bitrate))     # Kilo bit per seconds
                jitter = round(jitter)
                loss = int(loss_cnt)
                total = int(total_cnt)
 
                res = {"throughput": bitrate, "jitter": jitter , "loss": loss}
            #    print('match' + line)

            elif  re.search(end_st, line):
                #self.parse_state = iperf_srv.parse_state_kind.end

                print("# End iperf forwarding #")
        else:
          #  print('not match'+line)
            pass

        return res


def main(iperf_meta, output_path):
    app = iperf_srv( iperf_meta["port"], iperf_meta["interval"])
    for line in app.stream():
        exp_data = app.parse(line)

        if exp_data:
            now = datetime.datetime.now(datetime.UTC)
            text = '{}Z, {}, {}\n'.format(now.strftime('%Y-%m-%dT%H:%M:%S'), exp_data["throughput"], exp_data["jitter"])

            with open(output_path, 'a') as f:
                f.write(text)

            print(text)

if __name__ == "__main__":
    import argparse

    p =  argparse.ArgumentParser()

    p.add_argument("-port", "--connect_port", default=5201, type=int, help="iperf server port")
    p.add_argument("-intv", "--interval", default=10, type=float)

    p.add_argument("-path", "--output_path", default="log_shinkansen.csv", type=str, help="output file path")
    args = p.parse_args()

    iperf_meta = {}
    iperf_meta["port"] = args.connect_port
    iperf_meta["interval"] = args.interval

    main(iperf_meta, args.output_path)
