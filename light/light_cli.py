#!/usr/bin/env python3


import light.modeling.loading as load
from parlai.core.script import superscript_main as parlai_cli

"""
Extends the ParlAI CLI to make light datasets available
"""


def main():
    # TODO extend to support LIGHT deploy tasks
    load.register_all_agents()
    load.register_all_tasks()
    parlai_cli()


if __name__ == "__main__":
    main()
