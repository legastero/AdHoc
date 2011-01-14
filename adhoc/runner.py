"""
    Adhoc: A command-line XMPP ad-hoc command runner.
    Copyright (C) 2011 Lance Stout
    This file is part of Adhoc.

    See the file LICENSE for copying permission.
"""

import logging
import math
import sleekxmpp
from sleekxmpp.thirdparty.ordereddict import OrderedDict


log = logging.getLogger(__name__)


class AdHocRunner(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password, provider, command=None):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.provider = provider
        self.command = command

        self.register_plugin('xep_0030')
        self.register_plugin('xep_0004')
        self.register_plugin('xep_0050', module='adhoc.plugins.xep_0050')

        self.add_event_handler('session_start', self.session_start)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

        try:
            commands = self['xep_0050'].get_commands(self.provider, block=True)

            data = OrderedDict()
            num_data = OrderedDict()
            num = 0
            max_node = 0
            for command in commands['disco_items']['items']:
                data[command[1]] = {'name': command[2],
                                    'jid': command[0],
                                    'num': num}
                num_data[str(num)] = command[1]
                if len(command[1]) > max_node:
                    max_node = len(command[1])
                num += 1

            if not self.command:
                title = 'Available Commands for %s:' % self.provider
                print(title)
                print('-' * len(title))
                for (node, cmd) in data.items():
                    node = (' %%%ds' % max_node) % node
                    num  = ('%%%dd' % math.log10(len(data))) % cmd['num']
                    print('%s (%s) - %s' % (node, num, cmd['name']))
            elif self.command not in data and self.command in num_data:
                self.command = num_data[self.command]

            while self.command not in data and self.command not in num_data:
                self.command = raw_input("Select command (number or node name): ")

                if self.command not in data:
                    if self.command in num_data:
                        self.command = num_data[self.command]
                    else:
                        error_msg = "Invalid node name or command number: %s"
                        log.error(error_msg % self.command)
                        self.command = None

            command = data[self.command]

            title = 'Executing Command: %s' % command['name']
            print(title)
            print('-' * len(title))

            cmd = self['xep_0050'].run_command(command['jid'],
                                               self.command,
                                               block=True)

            while cmd['command']['status'] not in ['completed', 'canceled']:
                sessionid = cmd['command']['sessionid']
                form = cmd['command']['form']
                actions = cmd['command']['actions']

                answers = OrderedDict()
                for field in form['fields']:
                    field = field[1]
                    label = field['label']
                    if not label:
                        label = field['var']
                    if field['type'] == 'hidden':
                        answers[field['var']] = field['value']
                    elif field['type'] in ('', 'text-single', 'jid-single'):
                        answers[field['var']] = raw_input('%s: ' % label)
                    elif field['type'] in ('text-multi', 'jid-multi'):
                        answer = []
                        print('%s: (Two blank lines to end)' % label)
                        resp = None
                        blank = False
                        while True:
                            resp = raw_input()
                            answer.append(resp)
                            if resp:
                                blank = False
                            elif blank:
                                break
                            else:
                                blank = True

                        answers[field['var']] = answer
                    elif field['type'] == 'boolean':
                        answers[field['var']] = raw_input('%s: (y/n)' % label)

                submit = ''
                actions.insert(0, 'cancel')
                if len(actions) == 1:
                    actions.append('complete')
                for action in actions:
                    if action == 'cancel':
                        submit += '(C)ancel'
                    if action == 'prev':
                        submit += ' (P)rev'
                    if action == 'next':
                        submit += ' (N)ext'
                    if action == 'complete':
                        submit += ' (F)inish'

                next_action = None
                while not next_action:
                    action = raw_input('%s: ' % submit)
                    next_actions = {'n': 'next',
                                    'next': 'next',
                                    'p': 'prev',
                                    'prev': 'prev',
                                    'f': 'complete',
                                    'finish': 'complete',
                                    'complete': 'complete',
                                    'c': 'cancel',
                                    'cancel': 'cancel'}
                    next_action = next_actions[action.lower()]
                    if next_action not in actions:
                        next_action = None

                form = self['xep_0004'].makeForm('submit')
                for answer in answers:
                    form.addField(var=answer, value=answers[answer])

                cmd = self.Iq()
                cmd['to'] = command['jid']
                cmd['type'] = 'set'
                cmd['command']['sessionid'] = sessionid
                cmd['command']['node'] = self.command
                cmd['command']['action'] = next_action
                cmd['command'].append(form)
                cmd = cmd.send(block=True)
        except:
            self.disconnect()

        self.disconnect()
