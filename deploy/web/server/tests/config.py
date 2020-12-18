#!/usr/bin/env python3

TEST_TORNADO_SETTINGS = {
    "autoescape": None,
    "cookie_secret": "0123456789",
    "compiled_template_cache": False,
    "debug": "/dbg/" in __file__,
    "login_url": "/login",
    "template_path": get_path("static"),
}
