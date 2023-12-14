#! /usr/bin/env nix-shell
#! nix-shell -i python3 --packages python3

import os
import re
import sys

HACKMD_ID_TO_MDBOOK_PATH = {
    # The Arguments for Bounded Dynamic Availability and Finality Overrides
    'sYzi5RW-RKS1j20OO4Li_w': './the-arguments-for-bounded-dynamic-availability-and-finality-overrides.md',

    # Notes on Snap‑and‑Chat
    'PXs8SOMHQQ6uBs3GXNPQjQ': './notes-on-snap-and-chat.md',

    # The Crosslink Construction
    'JqENg--qSmyqRt_RqY7Whw': './construction.md',
    '@daira/SJ7dHPZlT': './construction.md',

    # Security Analysis of Crosslink
    'YboxY2yLQDujpdkHj7JNMA': './security-analysis.md',

    # Questions about Crosslink
    'L96pOB1nRdOOb1OHLL8_FA': './questions.md',

    # Potential Changes to Crosslink
    'n8ZDPeTRQj-wa7JWb293oQ': './potential-changes.md',
}

HACKMD_LINK_RGX = re.compile(
    r'\(https://hackmd\.io/([^)]+)\)'
)

HACKMD_LINK_PARTS_RGX = re.compile(
    r'(?P<ID>[^?]+)(\?view(?P<ANCHOR>[^)]*))?'
)

def main():
    for path, dirs, files in os.walk('./src'):
        for file in files:
            if file.endswith('.md'):
                rewrite_md_file(os.path.join(path, file))

def rewrite_md_file(path):
    with open(path, 'r') as f:
        text = f.read()
    (replacement, count) = replace_links(text)
    if count > 0:
        print(f'Rewriting {count} links in {path!r}...')
        with open(path, 'w') as f:
            f.write(replacement)

def replace_links(text):
    return HACKMD_LINK_RGX.subn(replace_link_match, text)

def replace_link_match(m):
    # We parse in two regex stages to ensure we process all hackmd links successfully:
    content = m.group(1)

    # Special case for hackmd image links:
    # Note: we link to hackmd.io directly for now as an expedient. In
    # a future change we should host the image within the book.
    if content.endswith('.png'):
        return f'(hackmd.io/{content})'

    m = HACKMD_LINK_PARTS_RGX.match(content)
    try:
        return replace_link_match_inner(m)
    except:
        (_, e, _) = sys.exc_info()
        e.args += (f'for input {content!r}',)
        raise

def replace_link_match_inner(m):
    assert m is not None
    id = m.group('ID')
    anchor = m.group('ANCHOR')
    mdpath = HACKMD_ID_TO_MDBOOK_PATH[id]
    anchor = anchor or ''
    assert anchor == '' or anchor.startswith('#')
    return f'({mdpath}{anchor})'

if __name__ == '__main__':
    main()
