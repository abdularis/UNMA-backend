# htmlfilter.py
# Created by abdularis on 22/10/17

import bleach
import bs4

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
    if name.lower() == 'style':
        styles = [s.lower().strip() for s in value.split(';') if s]
        for style in styles:
            pair = [s.strip() for s in style.split(':')]
            if tag == 'table':
                print(pair)
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
        print(img.get('style'))

    # style_tag = bs4.Tag(name='style')
    # style_tag.string = "img{max-width: 100%;max-height: 100%;}"
    # soup.insert(0, style_tag)

    return soup.decode()
