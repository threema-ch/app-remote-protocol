# Threema App Remote Protocol (ARP)

This documentation contains the specification of the data exchange protocol
used between the Threema apps and a remote client (e.g. Threema Web).

## Generating HTML Docs

Requirements:

- Python 3.6+
- pipenv

Setup:

    pipenv install

Run:

    pipenv run python generate.py

The static output is written to the `output/` directory.

## Schema Format

The schema is a custom YAML based format that can be parsed to generate HTML
docs. Descriptions and summaries may contain markdown (commonmark flavor)
markup.

## License

### Python Code (MIT)

Copyright © 2018 Threema GmbH (https://threema.ch/).

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

### Documentation Text (CC BY-SA 3.0)

Copyright © 2018 Threema GmbH (https://threema.ch/).

This work is licensed under the [Creative Commons Attribution-ShareAlike 3.0
Unported License](https://creativecommons.org/licenses/by-sa/3.0/). To view a
copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/ or
send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
