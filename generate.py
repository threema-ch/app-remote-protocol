import copy
import distutils.dir_util
import json
import os
from typing import List, Tuple

from jinja2 import Environment, FileSystemLoader

import filters


TEMPLATE_DIR = 'templates'
OUT_DIR = 'output'


def main(filename: str):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    env.filters['cmark'] = filters.commonmark
    env.filters['linkmodels'] = filters.linkmodels
    with open(filename, 'r') as f:
        schema = json.loads(f.read())
    process_includes(schema)
    process_replies(schema)
    copy_static_files()
    generate_index(env, schema)
    for typ, subtypes in schema['messages'].items():
        for subtype, messages in subtypes.items():
            for message in messages:
                generate_message(env, typ, subtype, message, schema['models'], schema['errorCodes'])
    for model, data in schema['models'].items():
        generate_model(env, model, data, [(k, v) for k, v in schema['models'].items()])
    for concept, data in schema['concepts'].items():
        generate_concept(env, concept, data)


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
                        try:
                            message['args']['fields'][i] = copy.copy(shared_fields[arg[1:]])
                        except KeyError:
                            raise RuntimeError(f'Shared arg field not found: {arg}')

                # Process data
                data = message.get('data', {}).get('fields', [])
                for i, datum in enumerate(data):
                    if isinstance(datum, str) and datum.startswith('@'):
                        try:
                            message['data']['fields'][i] = copy.copy(shared_fields[datum[1:]])
                        except KeyError:
                            raise RuntimeError(f'Shared data field not found: {datum}')


def process_replies(schema: dict):
    """
    Copy replies towards a specific message into the targeted message.
    """
    for typ, subtypes in schema['messages'].items():
        for subtype, messages in subtypes.items():
            for message in messages:
                if 'replyTo' in message:
                    for reply in message['replyTo']:
                        other_type, other_subtype = reply['message'].split('/')

                        # Store in other direction's message
                        direction = get_other_direction(message['direction'])
                        for other_message in schema['messages'][other_type][other_subtype]:
                            if other_message['direction'] == direction:
                                other_message.setdefault('__replyFrom', [])
                                other_reply = copy.deepcopy(reply)
                                other_reply['message'] = f'{typ}/{subtype}'
                                other_message['__replyFrom'].append(other_reply)


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
                models=schema['models'],
                concepts=schema['concepts'],
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


def get_reply_message(message_direction: str, reply_message: dict, error_codes: dict) -> dict:
    typ, subtype = reply_message['message'].split('/')
    reply_message['filename'] = f'message-{typ}-{subtype}-{message_direction}.html'
    reply_message.setdefault('condition', '(None)')
    reply_message.setdefault('errorCodes', {}).update(error_codes)
    return reply_message


def get_other_direction(direction: str) -> str:
    return {
        'bidirectional': 'bidirectional',
        'toapp': 'fromapp',
        'fromapp': 'toapp',
    }[direction]


def generate_message(env: Environment, typ: str, subtype: str, message: dict, models: dict, error_codes: dict):
    filename = f'message-{typ}-{subtype}-{message["direction"]}.html'
    template = 'message.html'
    print(f'Generating {filename}')
    template = env.get_template(template)
    direction_text = direction_to_text(message['direction'])
    
    reply = None
    if 'replyTo' in message:
        reply = {
            'direction': 'to',
            'message': message['replyTo'],
        }
    elif '__replyFrom' in message:
        reply = {
            'direction': 'from',
            'message': message['__replyFrom'],
        }
    if reply is not None:
        reply['message_direction'] = get_other_direction(message['direction'])
        reply['message_text_direction'] = direction_to_text(reply['message_direction'])
        reply['message'] = [get_reply_message(reply['message_direction'], reply_message, error_codes)
                            for reply_message in reply['message']]

    resolved_models = []
    if 'models' in message:
        for model in message['models']:
            resolved_models.append((model, models[model]))
            
    with open(os.path.join(OUT_DIR, filename), 'w') as f:
        f.write(
            template.render(
                title=f'Message: {typ} / {subtype} ({direction_text})',
                type=typ,
                subtype=subtype,
                message=message,
                reply=reply,
                models=resolved_models,
                error_codes=error_codes,
            )
        )


def generate_model(env: Environment, model: str, data: dict, models: List[Tuple[str, dict]]):
    filename = f'model-{model}.html'.lower()
    template = 'model.html'
    print(f'Generating {filename}')
    template = env.get_template(template)
    with open(os.path.join(OUT_DIR, filename), 'w') as f:
        f.write(
            template.render(
                title=f'Model: {model}',
                model=model,
                data=data,
                models=models,
            )
        )


def generate_concept(env: Environment, concept: str, data: dict):
    filename = f'concept-{concept}.html'.lower()
    template = 'concept.html'
    print(f'Generating {filename}')
    template = env.get_template(template)
    with open(os.path.join(OUT_DIR, filename), 'w') as f:
        f.write(
            template.render(
                title=f'Concept: {data["name"]}',
                data=data,
            )
        )


if __name__ == '__main__':
    if not os.path.exists('output'):
        os.makedirs('output')
    main('schema/v2.json')
