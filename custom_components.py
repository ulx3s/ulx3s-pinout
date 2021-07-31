import base64
import urllib.request

from pinout import templates
from pinout.core import SvgShape

class PNG_from_web(SvgShape):

    def __init__(self, path, embed=False, **kwargs):
        super().__init__(**kwargs)
        self.path = path
        self.svg_data = None
        self.embed = embed

    def render(self):
        """Linking or embed a PNG formatted image from a web url."""
        
        tplt = templates.get("image.svg")
        if self.embed:

            with urllib.request.urlopen(self.path) as f:
                imgdata = f.read()

            encoded_img = base64.b64encode(imgdata)
            self.path = f"data:image/png;base64,{encoded_img.decode('utf-8')}"

        return tplt.render(image=self)