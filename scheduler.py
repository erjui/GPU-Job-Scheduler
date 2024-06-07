from apscheduler.schedulers.background import BackgroundScheduler
import time
import logging
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
    for index in range(count):
        handle = nvidia_smi.nvmlDeviceGetHandleByIndex(index)
        meminfo = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
        meminfos.append(meminfo.used / 1024 / 1024)

    return meminfos

def main_scheduler(targets, thres=1000):
    scheduler.add_job(main_job, 'interval', seconds=5, args=[targets, thres], id='main_job')
    scheduler.start()

    try:
        while True:
            time.sleep(1)
            if len(scheduler.get_jobs()) == 0:
                break
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

def main_job(targets, thres):
    #! Load jobs queued
    # todo. queue should be different each unique server
    with open('queue.txt', 'r') as f:
        queue = f.read().splitlines()
        # queue = queue[1:]

    jobs = queue
    jobs = [e.split('#####') for e in jobs]

    #! Remove jobs not necessary
    occupied_gpus = []
    new_jobs = []
    for idx, job in enumerate(jobs):
        target = job[0]
        gpus = target.split(',')

        # if any of gpus in occupied gpus
        if any(e in occupied_gpus for e in gpus):
            continue

        occupied_gpus.extend(gpus)
        new_jobs.append([idx, job])

    #! Check the condition to run job
    runs = []
    for idx, job in new_jobs:
        target = job[0]
        command = job[1]

        meminfos = get_gpu_memory(targets)
        for i, meminfo in enumerate(meminfos):
            print(f"GPU {i}: {meminfo:.2f} MB")

        cnt = 0
        for meminfo in meminfos:
            if meminfo < thres:
                cnt += 1

        if cnt == len(targets):
            process = subprocess.Popen(command, shell=True)

            runs.append(idx)

    #! Remove batched jobs (disble when debugging 😱)
    with open('queue.txt', 'w') as f:
        for idx, job in enumerate(jobs):
            if idx not in runs:
                f.write(job[0] + '#####' + job[1] + '\n')
        f.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='GPU Memory Monitor')
    parser.add_argument('--targets', type=int, nargs='+', default=[0, 1, 2, 3], help='GPU indices to monitor')
    parser.add_argument('--thres', type=int, default=5000, help='Threshold to trigger training')
    args = parser.parse_args()

    print(f"Monitoring {args.targets} with threshold {args.thres}.")
    print(f"Press Ctrl+C to stop.")

    main_scheduler(args.targets, args.thres)