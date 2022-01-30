# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import json
import subprocess
from pathlib import Path
import logging

from .base import call, call_batch
from .plugin import start_with_cd, xls2dta, summary, reg, nbreg, psm
from .put import put_to_excel
from .data import use_data_config

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)s %(name)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt=r'%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG,
    filename=os.environ.get('LOG_FILE'),
    filemode='a',
)

STATA_ENTRY = os.environ.get('STATA_ENTRY', '/Applications/Stata/StataSE.app/Contents/MacOS/StataSE')
logger = logging.getLogger('stata')
logger.addHandler(logging.StreamHandler())


def run(working_dir):
    """ https://www.stata.com/support/faqs/mac/advanced-topics/
    """
    with open(os.path.join(working_dir, 'config.json')) as f:
        config = json.load(f)

    actions = [
        start_with_cd(working_dir),
    ]

    if config.get('data'):
        use_data_config(config['data'], working_dir)
        actions.append(call('use "use-data.dta"'))

    if os.path.exists(os.path.join(working_dir, 'use-data.xlsx')):
        actions.append(xls2dta('use-data.xlsx', 'use-data.dta'))

    for action in config['actions']:
        if action['type'] == 'summary':
            actions.append(summary(action['vars']))
        elif action['type'] == 'nbreg':
            actions.append(reg(action["vars"]))
            actions.append(nbreg(f'{action["depVar"]} {action["vars"]}'))
        elif action['type'] == 'psm':
            actions.append(psm(action["treatVar"], action["vars"], action["depVar"]))

    do_content = call_batch(*actions)
    do_file = os.path.join(working_dir, 'run.do')
    with open(do_file, 'w') as f:
        f.write(do_content)

    try:
        subprocess.call([
            STATA_ENTRY,
            '-b',
            '-e',
            'do',
            'run.do'
        ], cwd=working_dir, timeout=5 * 60)
        with open(os.path.join(working_dir, 'run.end'), 'w') as f:
            f.write('success')
        run_log = os.path.join(working_dir, 'run.log')
        if os.path.exists(run_log):
            with open(run_log, 'r') as f:
                put_to_excel(f.read(), os.path.join(working_dir, 'output.xlsx'))

    except subprocess.TimeoutExpired:
        logger.error(f'执行超时 {working_dir} subprocess.TimeoutExpired')
        with open(os.path.join(working_dir, 'run.end'), 'w') as f:
            f.write('error')


def run_all(entry_dir):
    # for dir_name in os.listdir(entry_dir):
    for file in Path(entry_dir).glob('**/config.json'):
        # working_dir = os.path.join(entry_dir, dir_name)
        working_dir = os.path.dirname(file)
        if not (os.path.isdir(working_dir)):
            continue
        logger.info(f'开始执行 {working_dir}...')
        run_end = os.path.join(working_dir, 'run.end')
        if os.path.exists(run_end):
            logger.info(f'忽略 {working_dir}')
            continue
        run(working_dir)


if __name__ == '__main__':
    run_all(os.environ['DIR_AUTOPROCESS'])
