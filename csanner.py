#!/usr/bin/env python3.2


from datetime import datetime
from os import environ, path
from os.path import join
from time import sleep
from sys import argv

import socket
import subprocess


HOMEDIR = environ.get('HOME')
SOUNDDIR = join(HOMEDIR, '.sound')
DEFSOUND = 'hitassist.wav'
EXTENSION = 'wav'

NICKNAMES = [b'NICKNAME1', b'NICKNAME2']
# CONNECT_IP = ["212.76.129.250", "89.44.246.11"]
CONNECT_IP = ["IP1_string", "IP2_string"]
# CONNECT_PORT = [27155, 27015]
CONNECT_PORT = [PORT1_int, PORT2_int]
CONNECT_SOCKET = tuple(zip(CONNECT_IP, CONNECT_PORT))

COLUMNWIDTH = 20
try:
    INTERVAL = int(argv[1])
    START_AFTER = int(argv[2])
except IndexError:
    INTERVAL = 30
    START_AFTER = 0
except ValueError:
    print('Must be integer')
    exit()

BASE = b"\xff\xff\xff\xff"


class Session:
    """docstring for Session"""
    MESSAGES = [BASE + b"\x69\x00"]
    MESSAGES.append(BASE + b"\x55" + BASE + b"\x00")

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(2)

    def get_4_bytes(self, ip=CONNECT_IP, port=CONNECT_PORT):
        """docstring for get_4_bytes"""
        self.sock.sendto(self.MESSAGES[1], (ip, port))
        return self.sock.recv(16)[-4:]
        # check it
        # 0f be 6a d9

    def get_answer(self, ip=CONNECT_IP, port=CONNECT_PORT):
        """docstring for get_answer"""
        self.MESSAGES.append(BASE + b"\x55" + self.get_4_bytes(ip, port))
        self.sock.sendto(self.MESSAGES[2], (ip, port))
        ans = self.sock.recv(1024)
        return ans

    def close(self):
        """docstring for close"""
        self.sock.close()


class TableView:
    """docstring for TableView"""
    def __init__(self, data, width):
        self.total = 0
        self.data = data
        self.width = width
        self.player_list = []
        self.time_now = datetime.now()

    def get_list(self, data):
        start_byte = 7
        lst = []
        while start_byte < len(data):
            null_byte = data.find(b'\x00', start_byte)
            lst.append(data[start_byte:null_byte])
            start_byte = null_byte+10
        self.total = len(lst)
        return lst

    def decor(self):
        """docstring for decor"""
        sep_line = ('+' + ('-' * self.width) + '+')
        print(sep_line)

        for i in self.player_list:
            try:
                print('{border}{nick}{border}'.format(
                    border='|', nick=str(i.decode('UTF-8')).ljust(self.width)))
            except UnicodeDecodeError:
                print("Undecodable Nickname''")

        print(sep_line)
        print('Всего: {tot}'.format(tot=self.total).center(self.width - 7) +
              '{h}:{m}:{s}'.format(
                  h=self.time_now.hour,
                  m=self.time_now.minute,
                  s=self.time_now.second,
                  ).rjust(1)
              )

    def view(self):
        """docstring for view"""
        self.player_list = self.get_list(self.data)
        return self.decor()

    def check(self):
        """docstring for check"""
        for nick in NICKNAMES:
            if nick in self.player_list:
                try:
                    self.alarm(join(SOUNDDIR, '{nick}.{ext}'.format(
                        nick=nick.decode('UTF-8'), ext=EXTENSION
                    )))
                except UnicodeDecodeError:
                    break

    def alarm(self, file=None):
        """docstring for fname"""
        if file is None or not path.isfile(file):
            file = join(SOUNDDIR, DEFSOUND)
        subprocess.call(['mplayer', '-really-quiet', '-vo', 'null',
                        '-ao', 'alsa', file])


def main():
    sleep(START_AFTER)
    while True:
        socket_ = CONNECT_SOCKET[0]
        s = Session()
        try:
            answer = s.get_answer(socket_[0], socket_[1])
            t = TableView(answer, COLUMNWIDTH)
            t.view()
            t.check()
        except socket.error as e:
            print(e)
        s.close()
        sleep(INTERVAL)

if __name__ == '__main__':
    main()
