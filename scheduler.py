import argparse
import datetime
import functools
import logging
import os
import subprocess
import sys
import time

import nvidia_smi
from apscheduler.schedulers.background import BackgroundScheduler
from colorama import init
from pyfiglet import figlet_format
from termcolor import cprint

from job import JobQueue


init(strip=not sys.stdout.isatty())
logging.basicConfig(level=logging.ERROR)

scheduler = BackgroundScheduler()
job_queue = None


def get_args():
    parser = argparse.ArgumentParser(description='GPU job scheduler')
    parser.add_argument('--thres', type=int, default=5000, help='Threshold to trigger job')
    parser.add_argument('--queue', type=str, default='queue.debug.json', help='Queue file path')
    return parser.parse_args()


def get_gpu_memory(targets=None):
    nvidia_smi.nvmlInit()
    if targets == None:
        count = nvidia_smi.nvmlDeviceGetCount()
        targets = list(range(count))

    meminfos = []
    for index in targets:
        handle = nvidia_smi.nvmlDeviceGetHandleByIndex(index)
        meminfo = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
        meminfo = {
            'used': meminfo.used / 1024 / 1024,
            'free': meminfo.free / 1024 / 1024,
            'total': meminfo.total / 1024 / 1024,
            'used_percent': meminfo.used / meminfo.total * 100,
            'free_percent': meminfo.free / meminfo.total * 100,
            'index': index,
            'name': nvidia_smi.nvmlDeviceGetName(handle),
        }
        meminfos.append(meminfo)

    return meminfos, targets


def main_scheduler(thres=1000, queue='queue.txt', interval=300):
    global job_queue

    job_queue = JobQueue(queue)
    scheduler.add_job(main_job, 'interval', seconds=interval, args=[thres], id='main_job', next_run_time=datetime.datetime.now())
    scheduler.start()

    try:
        while True:
            time.sleep(1)
            if len(scheduler.get_jobs()) == 0:
                break
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


def pre_exec(meminfos, thres):
    for meminfo in meminfos:
        print(f"GPU {meminfo['index']} ({meminfo['name']}): Used Memory [{meminfo['used']:.0f}/{meminfo['total']:.0f}] MB, Threshold: {thres} MB")
    print("New job is submitted successfully 🚀")


def main_job(thres):
    global job_queue

    #! Load jobs
    job_queue.load_jobs()
    job_queue.update_jobs()
    jobs = job_queue.get_jobs()
    valid_jobs = job_queue.get_valid_jobs()

    #! Run jobs
    runs = []
    for idx, job in valid_jobs:
        gpus, command, cwd = job.gpus, job.command, job.working_dir
        gpus = [int(gpu) for gpu in gpus.split(',')] if gpus else None

        meminfos, gpus = get_gpu_memory(gpus)

        cnt = 0
        for meminfo in meminfos:
            if meminfo['used'] < thres:
                cnt += 1

        if cnt == len(gpus):
            infos = functools.partial(pre_exec, meminfos, thres)
            env = {**os.environ, 'CUDA_VISIBLE_DEVICES': ",".join([str(gpu) for gpu in gpus])}
            process = subprocess.Popen(command, preexec_fn=infos, close_fds=True, cwd=cwd, env=env, shell=True)

            jobs[idx].process = process
            jobs[idx].status = 'running'
            runs.append(idx)

    #! Update jobs
    job_queue.jobs = [job for idx, job in enumerate(jobs) if idx not in runs]
    job_queue.running_jobs = [job for idx, job in enumerate(jobs) if idx in runs]
    job_queue.save_jobs()


def main():
    args = get_args()

    print(f"Running GPU job scheduler...")
    print("================================")
    print()

    cprint(figlet_format('GPU Job Scheduler!', font='larry3d'), attrs=['bold'])

    print("================================")
    print(f"Monitoring with threshold {args.thres}.")
    print(f"Press Ctrl+C to stop.")

    main_scheduler(args.thres, args.queue)


if __name__ == '__main__':
    main()
