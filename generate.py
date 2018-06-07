import copy
import distutils.dir_util
import json
import os

from jinja2 import Environment, FileSystemLoader

import filters


TEMPLATE_DIR = 'templates'
OUT_DIR = 'output'


def main(filename: str):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    env.filters['cmark'] = filters.commonmark
    with open(filename, 'r') as f:
        schema = json.loads(f.read())
    process_includes(schema)
    copy_static_files()
    generate_index(env, schema)
    for typ, subtypes in schema['messages'].items():
        for subtype, messages in subtypes.items():
            for message in messages:
                generate_message(env, typ, subtype, message)


def copy_static_files():
    distutils.dir_util.copy_tree('static/', 'output/static')


def process_includes(schema: dict):
    """
    Look for includes and replace them with the shared objects.
    """
    # Extract shared fields
    shared_fields = schema['sharedFields']
    del schema['sharedFields']

    # Process all messages
    for typ, subtypes in schema['messages'].items():
        for subtype, messages in subtypes.items():
            for message in messages:

                # Process args
                args = message.get('args', {}).get('fields', [])
                for i, arg in enumerate(args):
                    if isinstance(arg, str) and arg.startswith('@'):
                        message['args']['fields'][i] = copy.copy(shared_fields[arg[1:]])

                # Process data
                data = message.get('data', {}).get('fields', [])
                for i, datum in enumerate(data):
                    if isinstance(datum, str) and datum.startswith('@'):
                        message['data']['fields'][i] = copy.copy(shared_fields[datum[1:]])


def generate_index(env: Environment, schema: dict):
    filename = 'index.html'
    template = 'index.html'
    print(f'Generating {filename}')
    template = env.get_template(template)
    with open(os.path.join(OUT_DIR, filename), 'w') as f:
        f.write(
            template.render(
                title=schema['title'],
                description=schema['description'],
                version=schema['version'],
                messages=schema['messages'],
            )
        )


def direction_to_text(direction: str) -> str:
    if direction == 'fromapp':
        return 'app -> client'
    if direction == 'toapp':
        return 'client -> app'
    if direction == 'bidirectional':
        return 'bidirectional'
    return 'unknown'


def generate_message(env: Environment, typ: str, subtype: str, message: dict):
    filename = f'message-{typ}-{subtype}-{message["direction"]}.html'
    template = 'message.html'
    print(f'Generating {filename}')
    template = env.get_template(template)
    direction_text = direction_to_text(message['direction'])
    with open(os.path.join(OUT_DIR, filename), 'w') as f:
        f.write(
            template.render(
                title=f'{typ} / {subtype} ({direction_text})',
                type=typ,
                subtype=subtype,
                message=message,
            )
        )


if __name__ == '__main__':
    if not os.path.exists('output'):
        os.makedirs('output')
    main('schema/v2.json')
