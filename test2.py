import multiprocessing as mp
import os
import time


def print_my(x):
    print(x)
    time.sleep(1)
if __name__ == '__main__':
    processes = []
    # with mp.Pool(10) as pool:
    #     pool.map(print_my, list(range(10)))
    t1 = time.time()
    for i in range(4):
        for i in range(34):
            p = mp.Process(target=print_my, args=(i,))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()
    t2 = time.time()
    print(t2-t1)

    t1 = time.time()
    for i in range(50):
        print_my(i)

    t2 = time.time()
    print(t2-t1)