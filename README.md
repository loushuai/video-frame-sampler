# Video Frame Sampler
A lightweight video frame sampler. Support multiprocessing to improve the throughput.

## Usage
```
python3 main.py input.mp4 ./output_dir -p 1000 -w 2
```
This samples input.mp4 one frame per second, output to output_dir with sequence number as the file name, with 2 concurrent workers.
