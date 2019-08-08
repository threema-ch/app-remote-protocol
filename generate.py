# Copyright 2018-2019 Threema GmbH, all rights reserved.

import copy
import distutils.dir_util
import functools
import os
from typing import Callable, List, Tuple

import yaml
from jinja2 import Environment, FileSystemLoader

import filters


TEMPLATE_DIR = 'templates'
OUT_DIR = 'output'


def main(filename: str):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    env.filters['cmark'] = filters.commonmark
    env.filters['linkmodels'] = filters.linkmodels
    with open(filename, 'r') as f:
        schema = yaml.load(f)
    process_references(schema)
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


def get_file_name(message: str) -> str:
    typ, subtype, direction = message.split('/', maxsplit=2)
    return f'message-{typ}-{subtype}-{direction}.html'


def get_display_name(message: str) -> str:
    typ, subtype, *_ = message.split('/', maxsplit=2)
    return f'{typ}/{subtype}'


def direction_to_text(direction: str) -> str:
    if direction == 'fromapp':
        return 'app -> client'
    if direction == 'toapp':
        return 'client -> app'
    if direction == 'bidirectional':
        return 'bidirectional'
    return 'unknown'


def get_ref_direction(direction: str) -> str:
    return {
        'bidirectional': 'bidirectional',
        'toapp': 'fromapp',
        'fromapp': 'toapp',
    }[direction]


def process_message_reference(messages: List[dict], message: dict, typ: str, subtype: str, field: str, ref_field: str):
    if field in message:
        for item in message[field]:
            ref_type, ref_subtype = item['message'].split('/', maxsplit=1)
            try:
                ref_subtype, ref_direction = ref_subtype.split('/', maxsplit=1)
            except ValueError:
                ref_direction = get_ref_direction(message['direction'])
                item['message'] += f'/{ref_direction}'

            # Inject a couple of fields
            item['filename'] = get_file_name(item['message'])
            item['display_message'] = get_display_name(item['message'])
            item['display_direction'] = direction_to_text(ref_direction)

            # Store in other direction's message
            ref_messages = [ref_message for ref_message in messages[ref_type][ref_subtype]
                            if ref_message['direction'] == ref_direction]
            if len(ref_messages) == 0:
                raise RuntimeError(f'{field} reference could not be resolved: {reply["message"]}')
            elif len(ref_messages) != 1:
                raise RuntimeError(f'{field} reference resolved to multiple targets: {reply["message"]}')
            ref_message, *_ = ref_messages
            if ref_message['direction'] == ref_direction:
                ref_message.setdefault(ref_field, [])
                ref_item = copy.deepcopy(item)

                # Update fields (including injected ones)
                ref_item['message'] = f'{typ}/{subtype}/{message["direction"]}'
                ref_item['filename'] = get_file_name(ref_item['message'])
                ref_item['display_message'] = get_display_name(ref_item['message'])
                ref_item['display_direction'] = direction_to_text(message['direction'])

                ref_message[ref_field].append(ref_item)


def process_references(schema: dict):
    """
    Copy references (subscriptions or replies) towards a specific message into the targeted message.
    """
    for typ, subtypes in schema['messages'].items():
        for subtype, messages in subtypes.items():
            for message in messages:
                process_message_reference(schema['messages'], message, typ, subtype, 'replyTo', '__replyFrom')
                process_message_reference(schema['messages'], message, typ, subtype, 'subscribeTo', '__subscribeFrom')


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


def get_message_reference(message: dict, field: str, ref_field: str, post_process_func: Callable[[dict], dict]) -> dict:
    item = None
    if field in message:
        item = {
            'direction': 'to',
            'message': message[field],
        }
    elif ref_field in message:
        item = {
            'direction': 'from',
            'message': message[ref_field],
        }
    if item is not None:
        item['message'] = [post_process_func(element) for element in item['message']]
    return item


def get_subscribe_message(subscribe_message: dict) -> dict:
    default_condition = '(None)'
    subscribe_message.setdefault('condition', '(None)')
    subscribe_message.setdefault('condition', default_condition)
    return subscribe_message


def get_reply_message(reply_message: dict, error_codes: dict) -> dict:
    reply_message.setdefault('condition', '(None)')
    reply_message.setdefault('errorCodes', {}).update(error_codes)
    return reply_message


def generate_message(env: Environment, typ: str, subtype: str, message: dict, models: dict, error_codes: dict):
    filename = f'message-{typ}-{subtype}-{message["direction"]}.html'
    template = 'message.html'
    print(f'Generating {filename}')
    template = env.get_template(template)
    direction_text = direction_to_text(message['direction'])

    resolved_models = []
    if 'models' in message:
        for model in message['models']:
            resolved_models.append((model, models[model]))

    reply = get_message_reference(message, 'replyTo', '__replyFrom', functools.partial(get_reply_message, error_codes=error_codes))
    subscribe = get_message_reference(message, 'subscribeTo', '__subscribeFrom', get_subscribe_message)

    with open(os.path.join(OUT_DIR, filename), 'w') as f:
        f.write(
            template.render(
                title=f'Message: {typ} / {subtype} ({direction_text})',
                type=typ,
                subtype=subtype,
                message=message,
                reply=reply,
                subscribe=subscribe,
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
    main('schema/v2.yaml')
