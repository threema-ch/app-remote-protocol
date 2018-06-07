import CommonMark


def commonmark(value):
    parser = CommonMark.Parser()
    ast = parser.parse(value)

    renderer = CommonMark.HtmlRenderer()
    html = renderer.render(ast)

    return html
