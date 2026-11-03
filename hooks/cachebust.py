"""Append a content hash to extra CSS links so browsers never mix new HTML with a cached old stylesheet."""
import hashlib
import os
import re

_hashes = {}


def on_config(config):
    _hashes.clear()
    for css in config.extra_css:
        path = os.path.join(config.docs_dir, str(css))
        if os.path.isfile(path):
            with open(path, "rb") as f:
                _hashes[str(css)] = hashlib.sha256(f.read()).hexdigest()[:10]
    return config


def on_post_page(output, page, config):
    for css, digest in _hashes.items():
        output = re.sub(r'(href="[^"]*' + re.escape(css) + r')"', r'\1?v=' + digest + '"', output)
    return output
