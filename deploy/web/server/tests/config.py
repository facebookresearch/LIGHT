#!/usr/bin/env python3

import os.path
import inspect

def get_path(filename):
    cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    return os.path.join(cwd, filename)

TEST_TORNADO_SETTINGS = {
    "autoescape": None,
    "cookie_secret": "0123456789",
    "compiled_template_cache": False,
    "debug": "/dbg/" in __file__,
    "login_url": "/login",
    "template_path": get_path("static"),
}
