import uuid
import json
import subprocess
from typing import Dict
import socket
import tempfile
import shutil
import os
from . import messages
import tarfile

def working():
    HOST, PORT = "localhost", 8765
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(None)
    try:
        sock.connect((HOST, PORT))
        messages.put_message(sock, messages.REGISTER_WORKER, '')
        while 'connected':
            msg_type, data = messages.get_message(sock)
            if msg_type == messages.CONNECTION_END:
                print("Close signal from coordinator - closing")
                return
            print(f"Data {data}")
            if msg_type == messages.WORK:
                print("Received work")
                cmd = data
                with tempfile.TemporaryDirectory() as dirpath:
                    #FIXME:Actual command should be created here
                    with subprocess.Popen(cmd.replace("%OUTPUTDIR%", dirpath),
                            shell=True) as process:
                        process.wait()
                    with tarfile.open("TarName.tar.gz", "w:gz") as tar:
                        tar.add(dirpath, arcname="TarName")
                    with open("TarName.tar.gz", 'rb') as outputs:
                        messages.put_bytes(sock, bytes([messages.WORK_RESULT]) + outputs.read())
    finally:
        sock.close()
        print("Closed worker")


def main(args=None):
    working()

if __name__ == '__main__':
    main()