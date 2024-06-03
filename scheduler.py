from apscheduler.schedulers.background import BackgroundScheduler
import time
import logging

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

def run_training():
    import subprocess

    print("Training...")
    command = "your command to train"
    # command = "python trainer/train.py +experiment=cxr_medmae"
    # command = "python -c 'print(\"Hello World!\")'"
    process = subprocess.Popen(command, shell=True)
    process.wait()
    time.sleep(10)
    print("Training finished.")

    scheduler.remove_job('main_job')
    scheduler.print_jobs()

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
    global on_train

    if on_train == True:
        return

    meminfos = get_gpu_memory(targets)
    for i, meminfo in enumerate(meminfos):
        print(f"GPU {i}: {meminfo:.2f} MB")
    print()

    cnt = 0
    for meminfo in meminfos:
        if meminfo < thres:
            cnt += 1

    if cnt == len(targets):
        run_training()
        on_train = True


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='GPU Memory Monitor')
    parser.add_argument('--targets', type=int, nargs='+', default=[0, 1, 2, 3], help='GPU indices to monitor')
    parser.add_argument('--thres', type=int, default=5000, help='Threshold to trigger training')
    args = parser.parse_args()

    print(f"Monitoring {args.targets} with threshold {args.thres}.")
    print(f"Press Ctrl+C to stop.")

    main_scheduler(args.targets, args.thres)