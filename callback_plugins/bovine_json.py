# (c) 2017, Shaun Smiley <senorsmile@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import os

from ansible.plugins.callback import CallbackBase

debug=True
debug=False

flush_results=True
flush_results=False

log_results=True

default_json=True # default json blob at end of run
default_json=False

#output_file='./test.json'
#f = open(output_file, 'a')

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    #CALLBACK_TYPE = 'stdout'
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'json2'

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display)

        ## make sure our local log file directory exists
        log_file_path='/.ansible/bovine/'
        log_file_path = os.path.expanduser('~') + log_file_path
        print("bovine log_file_path = " + log_file_path)
        if not os.path.exists(log_file_path):
            os.makedirs(log_file_path)

        self.results = []

    def _new_play(self, play):
        return {
            'play': {
                'name': play.name,
                'id': str(play._uuid)
            },
            'tasks': []
        }

    def _new_task(self, task):
        return {
            'task': {
                'name': task.name,
                'id': str(task._uuid)
            },
            'hosts': {}
        }

    def v2_playbook_on_play_start(self, play):

        if debug:
            print("*** v2_runner_on_play_start")
            print("****** play=", play)
            print()
        elif flush_results or log_results:
            self._display.display(
                json.dumps(
                    {"PLAY: START": str(play)}, 
                    indent=4, 
                    sort_keys=True
                )
            )
        elif default_json:
            self.results.append(self._new_play(play))


    def v2_playbook_on_task_start(self, task, is_conditional):

        if debug:
            print("*** v2_playbook_on_task_start")
            print("****** task=", task)
            print()
        elif flush_results or log_results:
            self._display.display(json.dumps({"TASK: START": str(task)}, indent=4, sort_keys=True))
        elif default_json:
            self.results[-1]['tasks'].append(self._new_task(task))

    def v2_runner_on_ok(self, result, **kwargs):

        if debug:
            print("*** v2_runner_on_ok")
            #print("****** DIR result", dir(result))
            #methods=['_host', '_result', '_task', 'is_changed', 'is_failed', 'is_skipped', 'is_unreachable']

            print("****** result _host=", result._host )
            print("****** result _task=", result._task )

            #print("****** DIR result is_changed=", dir(result.is_changed) )
            #print("****** STR result is_changed=", str(result.is_changed) )

            print("****** result _result=", json.dumps(result._result, indent=4) )
            print("****** kwargs", kwargs)
            print()
        elif flush_results or log_results:
            if 'stdout' in result._result:
                del result._result['stdout']
            self._display.display(
                json.dumps(
                    {
                        "TASK: OK": {
                            str(result._host): result._result,
                        },
                    }, 
                    indent=4, 
                    sort_keys=True,
                )
            )
        elif default_json:
            host = result._host
            self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result

    def v2_playbook_on_stats(self, stats):
        """Display info about playbook statistics"""

        if debug:
            print("*** v2_playbook_on_stats")
            print("****** DIR stats=", dir(stats))
            print("****** changed stats=", stats.changed)
            print("****** failures stats=", stats.failures)
            print("****** ok stats=", stats.ok)
            print("****** skipped stats=", stats.skipped)
            print("****** processed stats=", stats.processed)
            print("****** dark stats=", stats.dark)
            print("****** custom stats=", stats.custom)
            print()
        elif default_json:
            hosts = sorted(stats.processed.keys())

            summary = {}
            for h in hosts:
                s = stats.summarize(h)
                summary[h] = s

            output = {
                'plays': self.results,
                'stats': summary
            }

            self._display.display(json.dumps({"PLAY RECAP": {}}, indent=4, sort_keys=True))
            self._display.display(json.dumps(output, indent=4, sort_keys=True))


    def v2_runner_on_failed(self, result, ignore_errors=False):
        if debug:
            print("*** v2_runner_on_failed")
            print("****** result._result=", result._result)
            print("****** result._task=", result._task)
            print()
        elif flush_results or log_results:
            if 'stdout' in result._result:
                del result._result['stdout']
            self._display.display(
                json.dumps(
                    {
                        "TASK: FAILED": {
                            str(result._host): result._result,
                        }
                    }, 
                    indent=4, 
                    sort_keys=True,
                )
            )
        elif default_json:
            host = result._host
            self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result

    def v2_runner_on_unreachable(self, result):
        if debug:
            print("*** v2_runner_on_unreachable")
            print("****** result._result=", result._result)
            print("****** result._task=", result._task)
            print()
        elif flush_results or log_results:
            if 'stdout' in result._result:
                del result._result['stdout']
            self._display.display(
                json.dumps(
                    {
                        "TASK: NODE UNREACHABLE": {
                            str(result._host): result._result,
                        },
                    }, 
                    indent=4, 
                    sort_keys=True,
                )
            )
        elif default_json:
            host = result._host
            self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result


    def v2_runner_on_skipped(self, result):
        if debug:
            print("*** v2_runner_on_skipped")
            print("****** result._result=", result._result)
            print("****** result._task=", result._task)
            print()
        elif flush_results or log_results:
            if 'stdout' in result._result:
                del result._result['stdout']
            self._display.display(
                json.dumps(
                    {
                        str(result._host): result._result,
                    }, 
                    indent=4, 
                    sort_keys=True,
                )
            )
        elif default_json:
            host = result._host
            self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result


    #v2_runner_on_failed = v2_runner_on_ok
    #v2_runner_on_unreachable = v2_runner_on_ok
    #v2_runner_on_skipped = v2_runner_on_ok
