# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import json
import subprocess

from .base import call_batch
from .plugin import start_with_cd, xls2dta, summary, reg, nbreg

STATA_ENTRY = os.environ.get('STATA_ENTRY', '/Applications/Stata/StataSE.app/Contents/MacOS/StataSE')


def run(working_dir):
    """ https://www.stata.com/support/faqs/mac/advanced-topics/
    """
    with open(os.path.join(working_dir, 'config.json')) as f:
        config = json.load(f)
    actions = [
        start_with_cd(working_dir),
        xls2dta('use-data.xlsx', 'use-data.dta'),
    ]
    for action in config['actions']:
        if action['type'] == 'summary':
            actions.append(summary(action['vars']))
        elif action['type'] == 'nbreg':
            actions.append(reg(action["vars"]))
            actions.append(nbreg(f'{action["depVar"]} {action["vars"]}'))

    do_content = call_batch(*actions)
    do_file = os.path.join(working_dir, 'run.do')
    with open(do_file, 'w') as f:
        f.write(do_content)
    subprocess.call([
        STATA_ENTRY,
        '-b',
        '-e',
        'do',
        'run.do'
    ], cwd=working_dir)


def run_all(entry_dir):
    for dir_name in os.listdir(entry_dir):
        working_dir = os.path.join(entry_dir, dir_name)
        if not (os.path.isdir(working_dir)):
            continue
        print(f'run with {working_dir}...')
        run(working_dir)


if __name__ == '__main__':
    run_all(os.environ['DIR_AUTOPROCESS'])
