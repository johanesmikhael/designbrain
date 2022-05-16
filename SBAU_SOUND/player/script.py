import os
import time
import pygame
import random
from glob import glob
import concurrent.futures
import requests
from requests.auth import HTTPBasicAuth

if __name__ == "__main__":
    print("SBAU 2021")


    if os.name == "nt":
        pass
    else:
        time.sleep(30)

    pygame.mixer.init(48000, -16, 2, 1024)

    if os.name == "nt":
        work_dir = os.getcwd()
    else:
        work_dir = os.path.normpath("/home/pi/VLC")

    sound_dir = os.path.join(work_dir, "sound")
    sound_path = os.path.join(sound_dir, "*.wav")

    sounds = sorted(glob(sound_path))

    snds = []
    channels = []
    for i, sound in enumerate(sounds):
        snds.append(pygame.mixer.Sound(sound))
        channels.append(pygame.mixer.Channel(i))

    channels[0].set_volume(1.0)
    channels[1].set_volume(1.0)
    channels[2].set_volume(1.0)
    channels[3].set_volume(1.0)

    for i in range(len(snds)):
        channels[i].play(snds[i], loops=-1)

    volume = [1.0, 1.0, 1.0, 1.0]

    patterns = [[1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
                [1, 1, 0],
                [0, 1, 1],
                [1, 0, 1]]

    c = [150, 151, 152
        , 155, 156, 157
        , 160, 161, 162
        , 165, 166, 167
        , 170, 171, 172
        , 175, 176, 177]
    e = [154, 158, 164, 168, 174, 178]
    k = [153, 159, 163, 169, 173, 179]


    def py_game():
        while pygame.mixer.get_busy():
            pattern = random.choice(patterns)
            for i in range(3):
                vol = pattern[i] * volume[i]
                channels[i+1].set_volume(vol)
            print(pattern)
            pygame.time.delay(30000)


    def stop_vlc(nums):
        for num in nums:
            ip = f"192.168.0.{num}"
            req = "http://" + ip + ":" + "8080" + "/requests/playlist.xml?command=pl_stop"
            password = "mxd"
            try:
                response =  requests.get(req, auth=HTTPBasicAuth('', password), timeout=1.0)
            except:
                print(f"failed: {ip}")

    def test_item(a, b):
        test = set(a) & set(b)
        if len(test) > 0:
            return True
        else:
            return False

    def text_loop():
        pc = pe = pk = [0, 0]
        nc = ne = nk = [0, 0]
        while True:
            while test_item(pc, nc):
                nc = random.sample(c, 1)
            while test_item(pe, ne):
                ne = random.sample(e, 1)
            while test_item(pk, nk):
                nk = random.sample(k, 2)
            pc = nc
            pe = ne
            pk = nk
            time.sleep(random.uniform(20,40))
            print( nc, ne , nk)
            stop_vlc(nc+ne+nk)

    def ping_loop():
        while True:
            response = os.system("ping -c 1 192.168.0.1")
            #and then check the response...
            if response == 0:
                pass
            else:
                print("reboot")
                if not os.name == "nt":
                    os.system("sudo reboot")
            time.sleep(300) # 300

    with concurrent.futures.ThreadPoolExecutor() as executor:
        f1 = executor.submit(py_game)
        f2 = executor.submit(text_loop)
        f3 = executor.submit(ping_loop)
