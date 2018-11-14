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
