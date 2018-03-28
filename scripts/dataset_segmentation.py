from cartotools.tools import image_pairs

from pathlib import Path
from typing import Iterator
from collections import defaultdict
import cv2

# python dataset_segmentation.py Haute-Garonne tags_airport.txt dataset_hg_airport_444  -l 1000
# python dataset_segmentation.py Toulouse tags_park.txt dataset_tls_park_444 -l 1000 -z 17+1

def make_slice(total: int, size: int, step: int) -> Iterator[slice]:
    for t in range(0, total - size, step):
        yield slice(t, t + size)
    if t + size < total:
        yield slice(total - size, total)


def dataset_segmentation(tag_file: Path, output_directory: Path,
                         location: str, zoom_level: int, augment: int,
                         service: str, cache_dir: Path, limit: int,
                         x_size: int, y_size: int, x_step: int, y_step: int):

    tags = dict()
    with tag_file.open('r') as fh:
        for line in fh.readlines():
            idx, tag = line.strip().split(' ')
            tags[int(idx)] = tag
            
    pairs = image_pairs(name=location, tag=tags,
                        zoom_level=zoom_level, augment=augment,
                        cache_dir=cache_dir, service=service)

    enumeration = range(limit) if limit > 0 else count(0)
    
    (output_directory / "img").mkdir(parents=True, exist_ok=True)
    (output_directory / "annot").mkdir(parents=True, exist_ok=True)
    
    img_list = []
    stats = defaultdict(int)
    for i, info in zip(enumeration, pairs):
        print(info[0])
        (x, y, z), (tile, mask) = info

        for x_ in make_slice(tile.shape[0], x_size, x_step):
            for y_ in make_slice(tile.shape[1], y_size, y_step):
                fname = f"{service}_{z}_{y}_{x}_{x_.start}_{y_.start}.png"
                
                tile_path = output_directory / "img" / fname
                cv2.imwrite(tile_path.as_posix(), tile[x_, y_, :])
                
                mask_path = output_directory / "annot" / fname
                cv2.imwrite(mask_path.as_posix(), mask[x_, y_])
                
                for tag in tags.keys():
                    stats[tag] += (mask==tag).sum()
                
                img_list.append(f"{tile_path.absolute().as_posix()} {mask_path.absolute().as_posix()}")
                            
    with (output_directory / "listings.txt").open('w') as fh:
        fh.write("\n".join(img_list))
        
    with (output_directory / "stats.txt").open('w') as fh:
        for k, v in stats.items():
            fh.write(f"label {k}: total: {v}, average: {v/len(img_list)}")

if __name__ == '__main__':
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Produce segmentation dataset")
    
    parser.add_argument("location", help="bounding box for the data")
    
    parser.add_argument("tag_file", type=Path,
                        help="path to the tag text file")
    
    parser.add_argument("output_directory", type=Path,
                       help="path to the output directory")
    
    parser.add_argument("-z", dest="zoom_level", default="13+1",
                       help="zoom level and augmentation (default: 13+1)")
    
    parser.add_argument("-t", dest="step", default="240x240",
                        help="step for the sliding window (default: 240x240)")
    
    parser.add_argument("-s", dest="size", default="480x480",
                        help="size for the output images (default: 480x480)")
    
    parser.add_argument("-i", dest="service", default="ArcGIS",
                        help="the source of data (default: ArcGIS)")
    
    parser.add_argument("-c", dest="cache_dir", default="/data1/sat", type=Path,
                        help="where to store the tiles (default: /data1/sat)")
    
    parser.add_argument("-l", dest="limit", default=0, type=int,
                        help="max number of images")
    
    args = vars(parser.parse_args())
    args['x_size'], args['y_size'] = \
        tuple(int(f) for f in args['size'].split('x'))
    args['x_step'], args['y_step'] = \
        tuple(int(f) for f in args['step'].split('x'))
    args['zoom_level'], args['augment'] = \
        tuple(int(i) for i in args['zoom_level'].split('+'))

    del args['size']
    del args['step']
    
    dataset_segmentation(**args)
    