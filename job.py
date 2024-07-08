import os


class Job:
    def __init__(self, gpus, command, working_dir, process=None):
        self.gpus = gpus
        self.command = command
        self.working_dir = working_dir

        self.status = 'ready'  # ready -> running -> terminated
        self.process = process

    def __str__(self):
        return f"{self.gpus}#####{self.command}#####{self.working_dir}"


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

        with open(self.queue_file, 'r') as f:
            lines = f.readlines()
            jobs = []
            for line in lines:
                line = line.strip()
                if len(line) == 0:
                    continue
                gpus, command, working_dir = line.split('#####')
                jobs.append(Job(gpus, command, working_dir))

            self.jobs = jobs
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
        with open(self.queue_file, 'w') as f:
            for job in self.jobs:
                f.write(str(job) + '\n')
            f.close()
