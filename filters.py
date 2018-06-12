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


def linkmodels(value: str, models):
    linked_models = [m[0] for m in models]
    match = MODEL_TYPE_RE.match(value)
    if match:
        (wrapper, model) = match.groups()
        if model in linked_models:
            return '{0}&lt;<a href="#model.{1}">{1}</a>&gt;'.format(
                escape(wrapper),
                escape(model),
            )
    return escape(value)
