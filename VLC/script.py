import os
import time
import random
from glob import glob
import sys

import requests
from requests.auth import HTTPBasicAuth
from xml.dom import minidom

import concurrent.futures

# from pynput.keyboard import Key, Listener

commands = dict()
commands['start'] = "?command=pl_play&id=0"
commands['start_r'] = "?command=pl_play&id="
commands['play'] = "?command=pl_play"
commands['pause'] = "?command=pl_pause"
commands['stop'] = "?command=pl_stop"
commands['next'] = "?command=pl_next"
commands['previous'] = "?command=pl_previous"
commands['sort'] = "?command=pl_sort&id=0&val=1"
commands['fullscreen'] = "?command=fullscreen"
commands['seek_to_zero'] = "?command=seek&val=0"
commands['vol_to_zero'] = "?command=volume&val=0"
commands['vol_to_full'] = "?command=volume&val=200"
commands['jump'] = f"?command=pl_play&id="
commands['seek'] = "?command=seek&val="
commands['check_status'] = ""

def individual_control(ip_port, url, req, password):
    ip, port = ip_port[0], ip_port[1]
    vlc_request = "http://" + ip + ":" + port + url + req
    try:
        response =  requests.get(vlc_request, auth=HTTPBasicAuth('', password), timeout=1.0)
    except :
        response = None
    return response


def control(command, args):
    commands, ip_ports, url, password = args[0], args[1], args[2], args[3]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        req = commands[command]
        _url = "http://" + ip + ":" + port + url + req
        future_to_ip_port = {executor.submit(individual_control, ip_port, url, req, password): ip_port for ip_port in ip_ports}
        response = {}
        for future in concurrent.futures.as_completed(future_to_ip_port):
            ip_port = future_to_ip_port[future]
            try:
                data = future.result()
            except:
                data = None
            response[ip_port] = data
        return response



def individual_jump(ip_port, url, commands, password):
    ip, port = ip_port[0], ip_port[1]
    vlc_playlist = "http://" + ip + ":" + port + "/requests/playlist.xml"
    vlc_status = "http://" + ip + ":" + port + "/requests/status.xml"
    to_play= []
    try:
        response =  requests.get(vlc_status, auth=HTTPBasicAuth('', password), timeout=1.0)
        status = minidom.parseString(response.text).getElementsByTagName('state')
        if status[0].firstChild.nodeValue == 'stopped':
            time.sleep(random.uniform(20.0, 30.0))
    except:
        return None
    try:
        response =  requests.get(vlc_playlist, auth=HTTPBasicAuth('', password), timeout=1.0)
        playlist = minidom.parseString(response.text).getElementsByTagName('leaf')
        for leaf in playlist:
            if leaf.getAttribute("current") == "":
                to_play.append(leaf.getAttribute("id"))
    except:
        return None
    if len(to_play) > 0:
        pid = random.choice(to_play)
        req = commands["jump"]
        seek = commands["seek"]
        vlc_request = "http://" + ip + ":" + port + url + req + pid
        seek_to = "http://" + ip + ":" + port + url + seek + f"{random.randrange(100)}%"
        try:
            response =  requests.get(vlc_request, auth=HTTPBasicAuth('', password), timeout=1.0)
            response =  requests.get(seek_to, auth=HTTPBasicAuth('', password), timeout=1.0)
            return response
        except :
            response = None
    else:
        return None

def random_jump(args):
    commands, ip_ports, url, password = args[0], args[1], args[2], args[3]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_ip_port = {executor.submit(individual_jump, ip_port,
        url, commands, password): ip_port for i, ip_port in enumerate(ip_ports)}
        response = {}
        for future in concurrent.futures.as_completed(future_to_ip_port):
            ip_port = future_to_ip_port[future]
            try:
                data = future.result()
            except:
                data = None
            response[ip_port] = data
        return response


def individual_start(ip_port, url, req, password):
    ip, port = ip_port[0], ip_port[1]
    vlc_playlist = "http://" + ip + ":" + port + "/requests/playlist.xml"
    to_play= []
    try:
        response =  requests.get(vlc_playlist, auth=HTTPBasicAuth('', password), timeout=1.0)
        playlist = minidom.parseString(response.text).getElementsByTagName('leaf')
        for leaf in playlist:
            to_play.append(leaf.getAttribute("id"))
    except:
        return None
    if len(to_play) > 0:
        pid = random.choice(to_play)
        vlc_request = "http://" + ip + ":" + port + url + req + pid
        try:
            response =  requests.get(vlc_request, auth=HTTPBasicAuth('', password), timeout=1.0)
            return response
        except :
            response = None
    else:
        return None

def random_start(args):
    commands, ip_ports, url, password = args[0], args[1], args[2], args[3]
    command = "start_r"
    with concurrent.futures.ThreadPoolExecutor() as executor:
        req = commands[command]
        future_to_ip_port = {executor.submit(individual_start, ip_port,
        url, req, password): ip_port for i, ip_port in enumerate(ip_ports)}
        response = {}
        for future in concurrent.futures.as_completed(future_to_ip_port):
            ip_port = future_to_ip_port[future]
            try:
                data = future.result()
            except:
                data = None
            response[ip_port] = data
        return response

def clear():
    # check and make call for specific operating system
    os.system('clear' if os.name =='posix' else 'cls')

if __name__ == "__main__":
    if os.name == "posix": # implementation mode in raspberry
        print("Design Brain Activated")
        time.sleep(30)
    # start vlc player
    if os.name == "nt":
        work_dir = os.getcwd()
    else:
        work_dir = os.path.normpath("/home/pi/VLC")
    media_dir = os.path.join(work_dir, "media")
    media_m3u = os.path.join(work_dir, "media.m3u")
    media_path = os.path.join(media_dir, "*")
    medias = sorted(glob(media_path))
    with open(media_m3u, "w") as f:
        for media in medias:
            f.write(f"{media}\n")
    print("start vlc")
    if os.name == "nt":
        print("windows nt detected")
        os.system(f"START vlc.exe -q --no-osd -L --no-video-title-show --http-port=8080 --repeat \"{media_m3u}\"")
    elif os.name == "posix":
        os.system(f"cvlc -q --no-osd -L --no-video-title-show --http-port=8080 --repeat \"{media_m3u}\" &")


    # addressing players
    ports = ["8080"]
    url = "/requests/status.xml"
    password = 'mxd'
    ip_ports = []
    ips = ["localhost"]
    for port in ports:
        for ip in ips:
            ip_ports.append((ip, port))
    args = [commands, ip_ports, url, password]

    text_dir = os.path.normpath("/home/pi/VLC/text")
    text_path = os.path.join(text_dir, "*.txt")
    txt_files = sorted(glob(text_path))
    random.shuffle(txt_files)
    txt_lines = []

    for txt in txt_files:
        with open(txt, 'r') as f:
            lines = f.readlines()
            lines = [l.strip("\n") for l in lines]
            txt_lines.extend(lines)
            txt_lines.append("\n")

    def text_loop():
        while True:
            for line in txt_lines:          # for each line of text (or each message)
                for c in line:          # for each character in each line
                    print(c, end='')    # print a single character, and keep the cursor there.
                    sys.stdout.flush()  # flush the buffer
                    time.sleep(random.uniform(0.02,0.05))          # wait a little to make the effect look good.
                print('')


    def video_loop():
        time.sleep(random.uniform(0,60))
        start = time.time()
        while True:
            # insert code for detecting stopping player and wait for a good 20-30 seconds
            # time.sleep(random.uniform(5.0, 10.0))
            response = random_jump(args)
            for k in response:
                # print(f"{k} : {response[k]}")
                if k == ('localhost', '8080'):
                    if response[k] is None:
                        print("local player is not detected, restart the system")
                        os.system("sudo reboot")
                    else:
                        status = minidom.parseString(response[k].text).getElementsByTagName('currentplid')
                        if int(status[0].firstChild.nodeValue) > 6:
                            time.sleep(random.uniform(11.0, 13.0))
                        else:
                            time.sleep(random.uniform(17.0, 19.0))


    def ping_loop():
    	while True:
    		response = os.system("ping -c 1 192.168.0.1")
    		#and then check the response...
    		if response == 0:
    			pass
    		else:
    			os.system("sudo reboot")
    		time.sleep(300)

    if os.name == "posix": # implementation mode in raspberry
        # time.sleep(5)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            f1 = executor.submit(text_loop)
            f2 = executor.submit(video_loop)
            f3 = executor.submit(ping_loop)
