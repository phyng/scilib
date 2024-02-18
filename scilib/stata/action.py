# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

from itertools import combinations
from .plugin import summary, reg, nbreg, psm, margins, label, teteffects, did


def use_actions(actions, config_actions):
    for action in config_actions:
        if action['type'] == 'summary':
            actions.append(summary(action['vars']))
        elif action['type'] == 'label':
            actions.append(label(action['name'], action['field'], action['values_map']))
        elif action['type'] == 'nbreg':
            actions.append(reg(f'{action["depVar"]} {action["vars"]}'))
            actions.append(nbreg(f'{action["depVar"]} {action["vars"]}'))
        elif action['type'] == 'reg':
            actions.append(reg(f'{action["depVar"]} {action["vars"]}', test=action.get("test", '')))
        elif action['type'] == 'margins':
            actions.append(margins(action["vars"], title=action.get('title'), xtitle=action.get('xtitle'), ytitle=action.get('ytitle')))  # noqa
        elif action['type'] == 'psm':
            actions.append(psm(action["treatVar"], action["vars"], action["depVar"]))
        elif action['type'] == 'teteffects':
            actions.append(teteffects(action["treatVar"], action["vars"], action["depVar"]))
        elif action['type'] == 'exec':
            """
            {
                "type": "exec",
                "command": "command"
            }
            """
            actions.append(action['command'])
        elif action['type'] == 'did':
            """
            {
                "type": "did",
                "time": "time",
                "treated": "treated",
                "y": "y",
                "cov": "x1 x2 x3"
            }
            """
            actions.append(did(action["time"], action["treated"], action["y"], action["cov"]))
        elif action['type'] == 'combinations':
            for var_list in combinations(action['vars'].split(), action['count']):
                for _action in action['actions']:
                    _new_action = {
                        **_action,
                        action['field']: ' '.join(var_list)
                    }
                    use_actions(actions, [_new_action])
