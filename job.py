import os


class Job:
    def __init__(self, gpus, command, working_dir):
        self.gpus = gpus
        self.command = command
        self.working_dir = working_dir

    def __str__(self):
        return f"{self.gpus}#####{self.command}#####{self.working_dir}"


class JobQueue:
    def __init__(self, queue_file):
        self.queue_file = queue_file
        self.jobs = self.load_jobs()

    def load_jobs(self):
        if not os.path.exists(self.queue_file):
            print("Job queue is not found 😱")
            print("Please create a queue file first.")
            return []

        with open(self.queue_file, 'r') as f:
            lines = f.readlines()
            jobs = []
            for line in lines:
                line = line.strip()
                if len(line) == 0:
                    continue
                gpus, command, working_dir = line.split('#####')
                jobs.append(Job(gpus, command, working_dir))
            return jobs

    def save_jobs(self):
        with open(self.queue_file, 'w') as f:
            for job in self.jobs:
                f.write(str(job) + '\n')
            f.close()
