"""
Helper script to add new message types.
"""
import json
import readline


def yn_choice(message, default='y'):
    choices = 'Y/n' if default.lower() in ('y', 'yes') else 'y/N'
    choice = input("%s (%s): " % (message, choices))
    values = ('y', 'yes', '') if choices == 'Y/n' else ('y', 'yes')
    return choice.strip().lower() in values


def fields(data: dict, key: str, name: str):
    category_desc = input(f'{name} description: ')
    if category_desc:
        data[key] = {'description': category_desc}
    else:
        data[key] = {}
    data[key]['fields'] = []
    while True:
        field = input(f'{name} field (enter to skip): ')
        if not field:
            break
        desc = input('  Description: ')
        typ = input('  Type: ')
        optional = yn_choice('  Optional', default='n')
        nullable = yn_choice('  Nullable', default='n')
        data[key]['fields'].append(
            {
                'field': field,
                'description': desc,
                'type': typ,
                'optional': optional,
                'nullable': nullable,
            }
        )
    if data[key]['fields'] == []:
        del data[key]['fields']
    if data[key] == {}:
        del data[key]


def main():
    # Main information
    direction = None
    while direction is None:
        val = input('Direction (fromapp|toapp|bidirectional): ')
        if val in ['fromapp', 'toapp', 'bidirectional']:
            direction = val
            break
    summary = input('Summary: ')

    data = {
        'direction': direction,
        'summary': summary,
    }

    # Add args and data
    fields(data, 'args', 'Args')
    fields(data, 'data', 'Data')

    # Add error codes
    error_codes = {'codes': {}}
    error_description = input('Error codes description: ')
    if error_description:
        error_codes['description'] = error_description
    while True:
        code = input('Error code (enter to skip): ')
        if not code:
            break
        desc = input('  Description: ')
        error_codes['codes'][code] = desc
    if error_codes['codes'] == {}:
        del error_codes['codes']
    if error_codes != {}:
        data['errorCodes'] = error_codes

    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nAborting.')
