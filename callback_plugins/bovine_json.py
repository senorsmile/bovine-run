# (c) 2017, Shaun Smiley <senorsmile@gmail.com>

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import os
from datetime import datetime

from ansible.plugins.callback import CallbackBase

debug=True
debug=False

flush_results=True
flush_results=False

log_results=True
logs_to_file=True

default_json=True # default json blob at end of run
default_json=False

#output_file='./test.json'
#f = open(output_file, 'a')


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'bovine_json'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display)

        if logs_to_file:
            # TODO: make log_file_path editable
            ## defaults to $HOME/.ansible/bovine
            log_file_path='/.ansible/bovine/'
            log_file_path = os.path.expanduser('~') + log_file_path

            print("bovine log_file_path = " + log_file_path)

            ## make sure our local log file directory exists
            if not os.path.exists(log_file_path):
                print("bovine lot_file_path does not exist.  Creating...")
                os.makedirs(log_file_path)

            ## open file for writing
            # TODO:
            now = datetime.now()
            now_str = now.strftime('%Y%m%d_%H%M%S')
            log_file = log_file_path + "bovine_run_" + now_str

            # open file in append mode
            # 0=unbuffered, i.e. flush on every write
            self.f = open(log_file, 'a', 0) 

        self.results = []

    def write_log(self,output):
        ## write output to log file
        self.f.write(output + "\n")

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
            output = json.dumps(
                {"PLAY: START": str(play)}, 
                indent=4, 
                sort_keys=True,
            )

            if flush_results: 
                self._display.display(output)

            if log_results:
                self.write_log(output)

        elif default_json:
            self.results.append(self._new_play(play))


    def v2_playbook_on_task_start(self, task, is_conditional):

        if debug:
            print("*** v2_playbook_on_task_start")
            print("****** task=", task)
            print()

        elif flush_results or log_results:
            output = json.dumps(
                {"TASK: START": str(task)}, 
                indent=4, 
                sort_keys=True,
            )

            if flush_results: 
                self._display.display(output)

            if log_results:
                self.write_log(output)

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
            ## what does this do?
            ## add comment once you figure it out
            ## maybe we delete stdout, since stdout_lines is better?
            if 'stdout' in result._result:
                del result._result['stdout']

            output = json.dumps(
                {
                    "TASK: OK": {
                        str(result._host): result._result,
                    },
                }, 
                indent=4, 
                sort_keys=True,
            )

            if flush_results: 
                self._display.display(output)

            if log_results:
                self.write_log(output)

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
        elif default_json or flush_results or log_results:
            hosts = sorted(stats.processed.keys())

            summary = {}
            for h in hosts:
                s = stats.summarize(h)
                summary[h] = s

            output = json.dumps(
                {
                    "PLAY: ALL DONE": {
                        'plays': self.results,
                        'stats': summary
                    }
                },
                indent=4, 
                sort_keys=True,
            )


            if flush_results or default_json: 
                self._display.display(output)

            if log_results:
                self.write_log(output)


    def v2_runner_on_failed(self, result, ignore_errors=False):
        if debug:
            print("*** v2_runner_on_failed")
            print("****** result._result=", result._result)
            print("****** result._task=", result._task)
            print()

        elif flush_results or log_results:
            if 'stdout' in result._result:
                del result._result['stdout']
            output = json.dumps(
                {
                    "TASK: FAILED": {
                        str(result._host): result._result,
                    }
                }, 
                indent=4, 
                sort_keys=True,
            )

            if flush_results: 
                self._display.display(output)

            if log_results:
                self.write_log(output)

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
            output = json.dumps(
                {
                    "TASK: NODE UNREACHABLE": {
                        str(result._host): result._result,
                    },
                }, 
                indent=4, 
                sort_keys=True,
            )

            if flush_results: 
                self._display.display(output)

            if log_results:
                self.write_log(output)

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

            output = json.dumps(
                {
                    str(result._host): result._result,
                }, 
                indent=4, 
                sort_keys=True,
            )

            if flush_results: 
                self._display.display(output)

            if log_results:
                self.write_log(output)

        elif default_json:
            host = result._host
            self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result

