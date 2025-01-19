import os
import cv2
from PIL import Image
import concurrent.futures
import shutil


def cv2pil(cv2_img):
    color_coverted = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(color_coverted)

    return pil_image


class Sampler():
    def __init__(self, input_file, output_path, per_msec, **kwargs) -> None:
        assert os.path.isfile(input_file), f"input file {input_file} does not exist"
        assert os.path.isdir(output_path), f"output path {output_path} is not a dir"

        self.input_file = input_file
        self.output_path = output_path
        self.per_msec = float(per_msec)
        capture = cv2.VideoCapture(self.input_file)
        self.total_frames = capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = capture.get(cv2.CAP_PROP_FPS)
        self.duration = round(self.total_frames / self.fps, 3)
        self.workers = kwargs.get("workers", 1)


    def get_duration(self):
        return self.duration


    def sample_between(self, start_frame=0, end_frame=-1, worker_id=0):
        capture = cv2.VideoCapture(self.input_file)

        if start_frame > 0:
            capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            assert start_frame == capture.get(cv2.CAP_PROP_POS_FRAMES), f"set frame to {start_frame} failed"

        count = 0
        id = 0
        success = True
        while success:
            if end_frame > 0 and capture.get(cv2.CAP_PROP_POS_FRAMES) >= end_frame:
                break

            success, frame = capture.read()

            if not success:
                break
            
            if count == 0:
                frame = cv2pil(frame)
                frame.save(os.path.join(self.output_path, f"{worker_id}_{id}.png"))

            count += 1
            if count * 1000 / self.fps >= self.per_msec:
                count = 0
                id += 1
            print(f"sample frame {capture.get(cv2.CAP_PROP_POS_FRAMES)}")

    def clear_up(self):
        files = [f for f in os.listdir(self.output_path) if (f.endswith("png") and "_" in f)]
        files.sort()
        for i, file in enumerate(files):
            shutil.move(os.path.join(self.output_path, file), os.path.join(self.output_path, f"{i}.png"))


    def execute(self):
        if self.workers == 1:
            self.sample_between()
        else:
            sample_frames_per_worker = self.total_frames // self.workers
            slices = []
            for i in range(self.workers-1):
                slices.append((i*sample_frames_per_worker, (i+1)*sample_frames_per_worker))
            slices.append(((self.workers-1)*sample_frames_per_worker, -1))
            slices = [s + (i, ) for i, s in enumerate(slices)]

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for i, s in enumerate(slices):
                    futures.append(executor.submit(self.sample_between, *s))
                for future in futures:
                    future.result()

        self.clear_up()
