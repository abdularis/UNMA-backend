# htmlfilter.py
# Created by abdularis on 22/10/17
import mimetypes

import bleach
import bs4
import io
import base64
from PIL import Image

MAX_IMAGE_WIDTH = 1000
DEFAULT_IMAGE_QUALITY = 55

ALLOWED_TAGS = [
    'blockquote',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'b', 'i', 'u',
    'ul', 'ol', 'li',
    'hr',
    'strong',
    'em',
    'a',
    'p',
    'code',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'img',
    'span',
    'pre'
]

ALLOWED_STYLE = [
    'font-family',
    'color',
    'background-color',
    'text-align',
    'font-weight',
    'width',
    'height',
    'margin', 'margin-left', 'margin-right',
    'text-decoration-line',
    'text-indent'
]


def filter_attributes(tag, name, value):
    """Filter attribute

        allowed attributes are 'style', 'width' and 'height'
        if the 'style' attribute has a property width & height in % the allow it,
        otherwise ignore this attribute
    """
    if name.lower() == 'style':
        styles = [s.lower().strip() for s in value.split(';') if s]
        for style in styles:
            pair = [s.strip() for s in style.split(':')]
            if len(pair) >= 2 and (pair[0] == 'width' or pair[0] == 'height'):
                return pair[1].endswith('%')
        else:
            return True
    return name in ['width', 'height']


ALLOWED_ATTRS = {
    '*': filter_attributes,
    'td': ['colspan', 'rowspan'],
    'a': ['href', 'target'],
    'img': ['src']
}

ALLOWED_PROTO = [
    'data'
]

# this css style is for styling html in client side/android web view
css_style_common = """
html {
    font-family: sans-serif;
    line-height: 1.5;
}
img {
    max-width: 100%;
    max-height: 100%;
}
"""

# this css style is for styling html in client side/android web view
css_style_table = """
table {
  border-spacing: 0;
  border-collapse: collapse;
}
.table {
  width: 100%;
  max-width: 100%;
  margin-bottom: 20px;
}
.table > thead > tr > th,
.table > tbody > tr > th,
.table > tfoot > tr > th,
.table > thead > tr > td,
.table > tbody > tr > td,
.table > tfoot > tr > td {
  padding: 8px;
  line-height: 1.42857143;
  vertical-align: top;
  border-top: 1px solid #ddd;
}
.table > thead > tr > th {
  vertical-align: bottom;
  border-bottom: 2px solid #ddd;
}
.table > caption + thead > tr:first-child > th,
.table > colgroup + thead > tr:first-child > th,
.table > thead:first-child > tr:first-child > th,
.table > caption + thead > tr:first-child > td,
.table > colgroup + thead > tr:first-child > td,
.table > thead:first-child > tr:first-child > td {
  border-top: 0;
}
.table > tbody + tbody {
  border-top: 2px solid #ddd;
}
.table .table {
  background-color: #fff;
}
.table-bordered {
  border: 1px solid #ddd;
}
.table-bordered > thead > tr > th,
.table-bordered > tbody > tr > th,
.table-bordered > tfoot > tr > th,
.table-bordered > thead > tr > td,
.table-bordered > tbody > tr > td,
.table-bordered > tfoot > tr > td {
  border: 1px solid #ddd;
}
.table-bordered > thead > tr > th,
.table-bordered > thead > tr > td {
  border-bottom-width: 2px;
}
"""

cleaner = bleach.Cleaner(
    tags=ALLOWED_TAGS,
    attributes=ALLOWED_ATTRS,
    styles=ALLOWED_STYLE,
    protocols=ALLOWED_PROTO,
    strip=True, strip_comments=True
)


def resize_image(image, scale_down_perc, quality):
    img_format = image.format
    if image.mode == 'RGB':
        img_format = "JPEG"
    if scale_down_perc < 100:
        new_size = tuple([int(elm / 100 * scale_down_perc) for elm in image.size])
        image = image.resize(new_size, Image.ANTIALIAS)
    new_resized_image = io.BytesIO()

    image.save(new_resized_image, format=img_format, optimize=True, quality=quality)
    return mimetypes.types_map.get('.{}'.format(img_format).lower()), new_resized_image


def resize_image_in_img_tag(img_tag):
    src = img_tag.get('src')
    if src:
        base64_img = src.split(',', 1)[1]
        bytes_img = base64.b64decode(base64_img)

        pil_image = Image.open(io.BytesIO(bytes_img))
        perc_scale = 95
        if pil_image.size[0] > MAX_IMAGE_WIDTH:
            perc_scale = MAX_IMAGE_WIDTH / pil_image.size[0] * 100

        mime, new_bytes_img = resize_image(pil_image, perc_scale, DEFAULT_IMAGE_QUALITY)

        info = 'data:%s;base64' % mime
        new_img_src = '{},{}'.format(info, str(base64.b64encode(new_bytes_img.getvalue()), 'utf-8'))
        img_tag['src'] = new_img_src


def filter_html(html):
    doc = cleaner.clean(html)
    soup = bs4.BeautifulSoup(doc, 'html.parser')
    for table in soup.find_all('table'):
        table['class'] = 'table table-bordered table-responsive'
    for img in soup.find_all('img'):
        style = 'max-width: 100%;max-height: 100%;'
        if img.get('style'):
            style += img.get('style')
        img['style'] = style

        try:
            resize_image_in_img_tag(img)
        except:
            print("Failed to resize an image")

    # style_tag = bs4.Tag(name='style')
    # style_tag.string = "img{max-width: 100%;max-height: 100%;}"
    # soup.insert(0, style_tag)

    return soup.decode()
