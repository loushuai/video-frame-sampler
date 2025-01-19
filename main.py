import os
import argparse
from sampler import Sampler


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help = "The path of input file")
    parser.add_argument("output", help = "The path of output dir")
    parser.add_argument("-p", "--permsec", required=True, type=int, help = "Sample interval in millisecond")
    parser.add_argument("-w", "--workers", default=1, type=int, help = "The number of workers, 0 to be cpu count. Default: 1")

    args = parser.parse_args()

    workers = args.workers if args.workers else os.process_cpu_count()
    sampler = Sampler(args.input, args.output, args.permsec, workers=workers)
    sampler.execute()
    
    print("done")
