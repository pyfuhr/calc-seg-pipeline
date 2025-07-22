import multiprocessing
from random import randint
import time

q = multiprocessing.Queue()
def start_subcalc(i):
    global q
    #time.sleep(randint(0, 10))
    for j in range(10):
        q.put((i, [randint(0,100) for j in range(10)]))

cores = 4
procs = []
for i in range(cores):
    p = multiprocessing.Process(target=start_subcalc, args=(i, ))
    p.start()

    procs.append(p)
while True:
    if all(not p.is_alive() for p in procs):
        break

with open(f'soap2_2x2arr.lst', 'w') as f:
    while not q.empty():
        i = q.get()
        f.write(f'{i[0]} {" ".join(map(str, i[1]))}\n')