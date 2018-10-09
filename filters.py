import re

import CommonMark
from jinja2 import escape


MODEL_TYPE_RE = re.compile(r'^([^<]*)<([^>]*)>$')


def commonmark(value):
    parser = CommonMark.Parser()
    ast = parser.parse(value)

    renderer = CommonMark.HtmlRenderer()
    html = renderer.render(ast)

    return html


def linkmodels(value: str, models, direct: bool = False):
    linked_models = [m[0] for m in models]
    match = MODEL_TYPE_RE.match(value)
    if match:
        (wrapper, model) = match.groups()
        if direct:
            link = 'model-{}.html'.format(escape(model).lower())
        else:
            link = '#model.{}'.format(escape(model))
        if model in linked_models:
            return '{0}&lt;<a href="{1}">{2}</a>&gt;'.format(
                escape(wrapper),
                link,
                escape(model),
            )
    return escape(value)

