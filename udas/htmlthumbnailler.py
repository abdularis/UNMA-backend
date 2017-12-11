# htmlthumbnailler.py
# Created by abdularis on 25/11/17
import io

from selenium import webdriver
from PIL import Image, ImageChops


def get_screenshot_from_html(html):
    browser = webdriver.PhantomJS()
    browser.get('data:text/html,%s' % html)
    return browser.get_screenshot_as_png()


def trim_whitespace(img):
    bbox = img.getbbox()
    if bbox:
        return img.crop(bbox)
    return img


def create_thumbnail_from_html(html, filename):
    image = Image.open(io.BytesIO(get_screenshot_from_html(html)))

    scaled_witdh = 200
    scale_factor = scaled_witdh * 100 / image.width

    new_size = (scaled_witdh, int(image.height * scale_factor / 100))
    image = image.resize(new_size, Image.ANTIALIAS)

    box_size = (0, 0, scaled_witdh, 260)
    thumbnail = image.crop(box_size)
    thumbnail = trim_whitespace(thumbnail)

    out_thumb = Image.new('RGB', thumbnail.size, (255, 255, 255))
    out_thumb.paste(thumbnail, mask=thumbnail.getchannel('A'))
    out_thumb.save(filename, format='JPEG', optimize=True, quality=50)
