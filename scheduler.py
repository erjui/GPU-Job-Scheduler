from apscheduler.schedulers.background import BackgroundScheduler
import os
import time
import datetime
import logging
import functools
import subprocess

# pip install apscheduler
# pip install nvidia-ml-py3

logging.basicConfig(level=logging.ERROR)

scheduler = BackgroundScheduler()
global on_train
on_train = False

def get_gpu_memory(targets=[0, 1, 2, 3]):
    import nvidia_smi

    nvidia_smi.nvmlInit()
    count = nvidia_smi.nvmlDeviceGetCount()

    meminfos = []
    for index in targets:
        handle = nvidia_smi.nvmlDeviceGetHandleByIndex(index)
        meminfo = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
        meminfos.append(meminfo.used / 1024 / 1024)

    return meminfos

def main_scheduler(thres=1000, queue='queue.txt', interval=300):
    scheduler.add_job(main_job, 'interval', seconds=interval, args=[thres, queue], id='main_job', next_run_time=datetime.datetime.now())
    scheduler.start()

    try:
        while True:
            time.sleep(1)
            if len(scheduler.get_jobs()) == 0:
                break
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

def pre_exec(gpus, meminfos, thres):
    for gpu, meminfo in zip(gpus, meminfos):
        print(f"GPU {gpu}: [{meminfo:.2f} / {thres}] MB")
    print("New job is submitted successfully 🚀")

def main_job(thres, queue):
    #! Load jobs queued
    if not os.path.exists(queue):
        print("Job queue is not found.")
        return

    with open(queue, 'r') as f:
        jobs = f.read().splitlines()
        jobs = [e.split('#####') for e in jobs]

    #! Remove jobs not necessary
    occupied_gpus = []
    new_jobs = []
    for idx, job in enumerate(jobs):
        gpus, command, _ = job
        gpus = gpus.split(',')

        # if any of gpus in occupied gpus
        if any(e in occupied_gpus for e in gpus):
            continue

        occupied_gpus.extend(gpus)
        new_jobs.append([idx, job])

    #! Check the condition to run job
    runs = []
    for idx, job in new_jobs:
        gpus, command, cmd = job
        gpus = gpus.split(',')
        gpus = [int(gpu) for gpu in gpus]

        meminfos = get_gpu_memory(gpus)

        cnt = 0
        for meminfo in meminfos:
            if meminfo < thres:
                cnt += 1

        if cnt == len(gpus):
            infos = functools.partial(pre_exec, gpus, meminfos, thres)
            process = subprocess.Popen(command, preexec_fn=infos, close_fds=True, cwd=cmd, shell=True)

            runs.append(idx)

    #! Remove batched jobs (disble when debugging 😱)
    with open(queue, 'w') as f:
        for idx, job in enumerate(jobs):
            if idx not in runs:
                f.write(job[0] + '#####' + job[1] + '#####' + job[2] + '\n')
        f.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='GPU job scheduler')
    parser.add_argument('--thres', type=int, default=5000, help='Threshold to trigger job')
    parser.add_argument('--queue', type=str, default='queue.txt', help='Queue file path')
    args = parser.parse_args()

    print(f"Monitoring with threshold {args.thres}.")
    print(f"Press Ctrl+C to stop.")

    main_scheduler(args.thres, args.queue)