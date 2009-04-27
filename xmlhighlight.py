import cgi

def make_span(contents, klass=None):
    return '<span%s>%s</span>' % (
        klass and (' class="%s"' % klass) or '',
        contents
    )

def attr_string(el):
    attrs = ' '.join([
        '%s="%s"' % (name, prepare_content(value))
        for name, value in el.attrib.items()
    ])
    if attrs:
        attrs = ' ' + attrs
    return '<span class="a">%s</span>' % attrs

def html_from_xml(root):
    html = ['<li>']
    html.append(make_span('&lt;%s%s&gt;' % (
        root.tag,
        attr_string(root)
    ), 't'))
    closing_tag = make_span('&lt;/%s&gt;' % root.tag, 't')
    children = root.getchildren()
    if children:
        html.append('<li>')
        html.append('<ol>')
        for child in children:
            html.append(html_from_xml(child))
        html.append('</ol>')
        html.append('</li>')
        html.append('<li>' + closing_tag + '</li>')
    else:
        s = ''.join(extract_text(root))
        if s:
            html.append(make_span(prepare_content(s), 'c'))
        html.append(closing_tag)
    
    html.append('</li>\n')
    return ''.join(html)

def extract_text(el, _addtail=False):
    result = []
    if el.text is not None:
        result.append(el.text)
    for elem in el:
        result.extend(elem.textlist(True))
    if _addtail and el.tail is not None:
        result.append(el.tail)
    return result

def prepare_content(text):
    text = cgi.escape(text)
    if text.startswith("http:"):
        klass = ''
        href = text
        if href.startswith('http://api.qype.com'):
            href = href.replace('http://api.qype.com/', '/')
            klass = ' class="apilink"'
        return '<a href="%s"%s>%s</a>' % (href, klass, text)
    else:
        return text

def highlight(el):
    return '<ol>' + html_from_xml(el) + '</ol>'
