from pathlib import Path

import matplotlib.pyplot as plt

from cartotools.tools import image_pairs


def test_image_pairs(name: str, tag: str, zoom_level: int,
                     cache_dir: Path, service: str, size: int,
                     output_file: Path) -> None:

    pairs = image_pairs(name=name, tag=tag, zoom_level=zoom_level,
                        cache_dir=cache_dir, service=service)

    fig, ax = plt.subplots(size, 2, figsize=(10, 25))

    for i, (tile, mask) in zip(range(size), pairs):
        ax[i, 0].imshow(tile,)
        ax[i, 1].imshow(mask, origin='lower')
        ax[i, 0].axis('off')
        ax[i, 1].axis('off')


    fig.tight_layout()
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    if output_file is None:
        fig.show()
    else:
        fig.savefig(output_file.as_posix())


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Produce test images")

    parser.add_argument("name", default="Toulouse",
                        help="place defining the bounding box")
    parser.add_argument("tag", help="name of the openstreetmap tag")
    parser.add_argument("-z", dest="zoom_level", default=13, type=int,
                        help="zoom level")
    parser.add_argument("-o", dest="output_file", type=Path,
                        default="output.png")
    parser.add_argument("-c", dest="cache_dir", type=Path,
                        default="/data1/sat")
    parser.add_argument("-s", dest="service", default="ArcGIS",
                        help="tiles provider (default: ArcGIS)")
    parser.add_argument("-n", dest="size", default=5, type=int,
                        help="number of samples")


    test_image_pairs(**vars(parser.parse_args()))
