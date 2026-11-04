"""Temporarily load CPU to test HighWindowsCpu with real host measurements."""
import multiprocessing as mp
import time


def work(seconds):
    end = time.monotonic() + seconds
    value = 1
    while time.monotonic() < end:
        value = (value * 1103515245 + 12345) & 0x7fffffff


if __name__ == "__main__":
    jobs = [mp.Process(target=work, args=(45,)) for _ in range(mp.cpu_count())]
    for job in jobs:
        job.start()
    for job in jobs:
        job.join()
