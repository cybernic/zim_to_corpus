#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Stuff used for HTML parsing."""

import re
from typing import Generator, Union

from bs4 import BeautifulSoup
from bs4.element import Tag

# Pattern for recognizing headers
headerp = re.compile('[hH][0-9]+')
# Pattern for recognizing lists
listp = re.compile('[ou]l')


def get_title(section: Tag) -> str:
    """Returns the title of the section."""
    for child in section.children:
        if headerp.match(child.name):
            return child.get_text()
    else:
        raise ValueError('No header in section')


def sections_backwards(tree: Union[BeautifulSoup, Tag]) -> Generator[Tag, None, None]:
    """Enumerates the sections in a document or HTML tree in reverse order."""
    if isinstance(tree, BeautifulSoup):
        yield from sections_backwards(tree.body)
    for child in tree.contents[::-1]:
        if isinstance(child, Tag) and child.name == 'section':
            yield from sections_backwards(child)
    else:
        if tree.name == 'section':
            yield tree
