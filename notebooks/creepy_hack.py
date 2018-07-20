from cartotools.img_tiles import IGN

class IGN_Ortho_2016(IGN):
    
    def _image_url(self, tile):
        x, y, z = tile
        url = "https://proxy-ign.openstreetmap.fr/94GjiyqD/bdortho/%s/%s/%s.jpg" % (z, x, y)
        return url

    def __init__(self):
        super().__init__(layer_name="")
        self.params['headers'] = {
            "Accept": "image/webp,image/*,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "en-US,en;q=0.8,fr;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            'Host': 'proxy-ign.openstreetmap.fr',
            'Referer': 'https://www.openstreetmap.org/id'
        }