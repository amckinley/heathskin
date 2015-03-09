import time
import subprocess
import select

f = subprocess.Popen(['tail','-F', "/var/log/daily.out"],\
        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
p = select.kqueue()
p.register(f.stdout)

while True:
    if p.poll(1):
        print f.stdout.readline()
    time.sleep(1)