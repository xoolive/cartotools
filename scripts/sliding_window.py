from pathlib import Path
from typing import Iterator

import cv2
from tqdm import tqdm


def make_slice(total: int, size: int, step: int) -> Iterator[slice]:
    for t in range(0, total - size, step):
        yield slice(t, t + size)
    if t + size < total:
        yield slice(total - size, total)


def _core_sliding(filename: Path, output_directory: Path,
                  x_size: int, y_size: int, x_step: int, y_step: int) -> None:

    if not filename.exists():
        raise RuntimeError(f"File {filename} does not exist")

    if output_directory.exists() and not output_directory.is_dir():
        raise RuntimeError(f"{output_directory} exists but is not a directory")

    if not output_directory.exists():
        output_directory.mkdir(parents=True)

    img = cv2.imread(filename.as_posix())

    if img is None:
        raise RuntimeError(f"Failed to open file {filename}")

    if (x_size > img.shape[0]) or (y_size > img.shape[1]):
        raise RuntimeError(f"Image {filename} {img.shape[:2]} is smaller than"
                           f"desired shape {x_size, y_size}")

    for x_ in make_slice(img.shape[0], x_size, x_step):
        for y_ in make_slice(img.shape[1], y_size, y_step):
            fname = f"{filename.stem}_{x_.start}_{y_.start}{filename.suffix}"
            path = output_directory / fname
            cv2.imwrite(path.as_posix(), img[x_, y_, :])


def sliding_window(filename: Path, output_directory: Path, extension: str,
                   x_size: int, y_size: int, x_step: int, y_step: int) -> None:
    if filename.is_dir():
        filelist = list(filename.glob(f"**/*.{extension}"))
        for file in tqdm(filelist):
            _core_sliding(file, output_directory,
                          x_size, y_size, x_step, y_step)
    else:
        _core_sliding(filename, output_directory,
                      x_size, y_size, x_step, y_step)


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(
        description="Pass a sliding window on an image"
    )

    parser.add_argument("-t", dest="step", default="100x100",
                        help="step for the sliding window (default: 100x100)")

    parser.add_argument("-s", dest="size", default="480x480",
                        help="size for the output images (default: 480x480)")

    parser.add_argument("-x", dest="extension", default="png",
                        help="extension for globbing images in directory")

    parser.add_argument("filename", type=Path,
                        help="path to the input image (or directory)")

    parser.add_argument("output_directory", type=Path, default="output",
                        help="directory for output files")

    args = vars(parser.parse_args())
    args['x_size'], args['y_size'] = \
        tuple(int(f) for f in args['size'].split('x'))
    args['x_step'], args['y_step'] = \
        tuple(int(f) for f in args['step'].split('x'))

    del args['size']
    del args['step']

    sliding_window(**args)
