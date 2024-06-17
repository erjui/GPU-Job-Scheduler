import argparse
import os
import shutil


def get_args():
    parser = argparse.ArgumentParser(description='Submit a job to the queue')
    parser.add_argument('--src', required=True, help='The source directory to copy')
    parser.add_argument('--dst', required=True, help='The destination directory where the source will be copied')
    parser.add_argument('--gpus', default='', help='The destination directory where the source will be copied')
    parser.add_argument('--command', required=True, help='The command to append to the queue file')
    parser.add_argument('--working_dir', required=True, help='The working directory where the command will be executed')
    parser.add_argument('--queue', default='queue.txt', help='The queue file to append the command')
    return parser.parse_args()


def copy2_verbose(src, dst):
    print('Copying {0}'.format(src))
    shutil.copy2(src, dst)


def copy_directory(src, dst):
    if not os.path.exists(src):
        print(f"Source directory '{src}' does not exist. Skipping... 🤷")
        return False
    if os.path.exists(dst):
        print(f"Destination directory '{dst}' already exists. Skipping... 🤷")
        return False
    shutil.copytree(src, dst, copy_function=copy2_verbose)
    print(f"Copied '{src}' to '{dst}' 🚀")
    return True


def append_command_to_queue(gpus, command, working_dir, queue):
    with open(queue, 'a') as f:
        f.write(f"{gpus}#####{command}#####{working_dir}\n")
    print(f"Appended job to '{queue}' 🚀")


def main():
    args = get_args()
    if copy_directory(args.src, args.dst):
        append_command_to_queue(args.gpus, args.command, args.working_dir, args.queue)


if __name__ == "__main__":
    main()
