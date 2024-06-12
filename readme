# 🚀 GPU Job Scheduler

A utility to automatically run commands depending on the GPU resources available.
Enslave your GPU work till the evitable death! 🖥️⚡

## ✨ Features
- Automatically schedules and runs jobs based on GPU availability. No more manual juggling!
- Easy to configure and extend for various types of jobs.

## 🔧 Installation

1. **Clone the repository:**
   ```sh
   git clone <repository_url>
   ```
2. **Install the required dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

## 🚀 Usage

Want to know more about how to use the scheduler? Just run:
```sh
python scheduler.py --help
```
This will display the help message with all available options and usage instructions.

### 🗂 `queue.txt` Format

Your `queue.txt` file should look like this:
```
[gpus]#####[commands]#####[working_directory]
```
For example:
```
0,1,2,3#####python -c 'print("hello, world")'#####/home
```

### 🎬 Running the Scheduler

Ready to roll? Use the following command:
```sh
python scheduler.py --thres <threshold> --queue <queue.txt>
```
- `threshold`: GPU threshold in MB.
- `queue`: Queue file to run jobs.

## 🤝 Contributing

Got ideas? Contributions are welcome! Please submit a pull request or open an issue to discuss any changes. 🌟
