import json
import os


class Job:
    def __init__(self, gpus, command, working_dir, process=None):
        self.gpus = gpus
        self.command = command
        self.working_dir = working_dir

        self.status = 'ready'  # ready -> running -> terminated
        self.process = process

    def __str__(self):
        msg = f"GPUs: {self.gpus}\nCommand: {self.command}\nWorking Dir: {self.working_dir}\nStatus: {self.status}"
        return msg

    def convert_to_json(self):
        return {
            'gpus': self.gpus,
            'command': self.command,
            'working_dir': self.working_dir,
        }


class JobQueue:
    def __init__(self, queue_file):
        self.queue_file = queue_file
        self.jobs = []
        self.running_jobs = []

    def get_jobs(self):
        return self.jobs

    def get_valid_jobs(self):
        occupied_gpus = []
        new_jobs = []
        for idx, job in enumerate(self.jobs):
            gpus = job.gpus
            gpus = gpus.split(',')

            # if any of gpus in occupied gpus
            if any(e in occupied_gpus for e in gpus):
                continue

            occupied_gpus.extend(gpus)
            new_jobs.append([idx, job])

        return new_jobs

    def load_jobs(self):
        if not os.path.exists(self.queue_file):
            print("Job queue is not found 😱")
            print("Please create a queue file first.")

            self.jobs = []
            return self.jobs

        self.jobs = read_json(self.queue_file)
        self.jobs = [Job(job['gpus'], job['command'], job['working_dir']) for job in self.jobs]
        return self.jobs

    def update_jobs(self):
        new_running_jobs = []
        for job in self.running_jobs:
            if job.status == 'running':
                if job.process.poll() is not None:
                    job.status = 'terminated'
                else:
                    new_running_jobs.append(job)
        self.running_jobs = new_running_jobs

    def save_jobs(self):
        write_json(self.queue_file, [job.convert_to_json() for job in self.jobs])


def read_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return []


def write_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def append_to_json(file_path, new_data):
    data = read_json(file_path)
    if isinstance(data, list):
        data.append(new_data)
    else:
        print("Error: JSON file does not contain a list.")
        return
    write_json(file_path, data)
