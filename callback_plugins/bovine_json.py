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

        self.start_time        =  datetime.now()
        self.start_time_str    =  self.start_time.strftime('%Y%m%d_%H%M%S')
        self.start_time_pretty =  self.start_time.strftime('%Y-%m-%d %H:%M:%S')

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
            log_file = log_file_path + "bovine_run_" + self.start_time_str

            print("bovine log_file = " + log_file)

            # open file in append mode
            # 0=unbuffered, i.e. flush on every write
            self.f = open(log_file, 'a', 0) 

        self.results = []

        ## set up vars to track which play and task we're in
        self.playname = None
        self.taskname = None


        if debug:
        ## print out initial data
            print("*** manual output: start of ansible")
            print()

        elif default_json or flush_results or log_results:
            output = json.dumps(
                { 
                    "type": "ANSIBLE START", 
                    "contents": {
                        'start_time': self.start_time_pretty,
                    },
                }, 
                indent=4, 
                sort_keys=False,
            )

            if flush_results or default_json: 
                self._display.display(output)

            if log_results:
                self.write_log(output)


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

    #--------------------------------------
    # play started
    #--------------------------------------
    def v2_playbook_on_play_start(self, play):
        self.playname = play.name

        if debug:
            print("*** v2_runner_on_play_start")
            print("****** play=", play)
            print()

        elif flush_results or log_results:
            output = json.dumps(
                { 
                    "type": "PLAY START", 
                    "name": play.name,
                    "contents": str(play),
                }, 
                indent=4, 
                sort_keys=False,
            )

            if flush_results: 
                self._display.display(output)

            if log_results:
                self.write_log(output)

        elif default_json:
            self.results.append(self._new_play(play))


    #--------------------------------------
    # task started
    #--------------------------------------
    def v2_playbook_on_task_start(self, task, is_conditional):
        self.taskname = task.name

        if debug:
            print("*** v2_playbook_on_task_start")
            print("****** task=", task)
            print()

        elif flush_results or log_results:
            output = json.dumps(
                { 
                    "type": "TASK START",
                    "name": task.name,
                    "contents": str(task),
                    "id": str(task._uuid),
                    "role": str(task._role),
                    "play": self.playname,
                }, 
                indent=4, 
                sort_keys=False,
            )

            if flush_results: 
                self._display.display(output)

            if log_results:
                self.write_log(output)

        elif default_json:
            self.results[-1]['tasks'].append(self._new_task(task))

    #--------------------------------------
    # task ok (per host)
    #--------------------------------------
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
                    "type": "TASK OK", 
                    "host": str(result._host),
                    "name": result.task_name,
                    "contents": result._result,
                    "play": self.playname,
                    "task": self.taskname,
                }, 
                indent=4, 
                sort_keys=False,
            )

            if flush_results: 
                self._display.display(output)

            if log_results:
                self.write_log(output)

        elif default_json:
            host = result._host
            self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result

    #--------------------------------------
    # item ok
    #--------------------------------------
    def v2_runner_item_on_ok(self, result, **kwargs):
        output = json.dumps(
            { 
                "type": "TASK ITEM OK", 
                "host": str(result._host),
                "contents": result._result,
                "name": str(result.task_name),
                "play": self.playname,
                "task": self.taskname,
            }, 
            indent=4, 
            sort_keys=False,
        )

        self.write_log(output)

    #--------------------------------------
    # item failed
    #--------------------------------------
    def v2_runner_item_on_failed(self, result, **kwargs):
        output = json.dumps(
            { 
                "type": "TASK ITEM FAILED", 
                "host": str(result._host),
                "name": str(result.task_name),
                "contents": result._result,
                "play": self.playname,
                "task": self.taskname,
            }, 
            indent=4, 
            sort_keys=False,
        )

        self.write_log(output)

    #--------------------------------------
    # item skipped 
    #--------------------------------------
    def v2_runner_item_on_skipped(self, result, **kwargs):
        output = json.dumps(
            { 
                "type": "TASK ITEM SKIPPED", 
                "host": str(result._host),
                "name": str(result.task_name),
                "contents": result._result,
                "play": self.playname,
                "task": self.taskname,
            }, 
            indent=4, 
            sort_keys=False,
        )

        self.write_log(output)



    #--------------------------------------
    # failed
    #--------------------------------------
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
                    "type": "TASK ITEM FAILED", 
                    "host": str(result._host),
                    "name": str(result.task_name),
                    "contents": result._result,
                    "play": self.playname,
                    "task": self.taskname,
                }, 
                indent=4, 
                sort_keys=False,
            )

            if flush_results: 
                self._display.display(output)

            if log_results:
                self.write_log(output)

        elif default_json:
            host = result._host
            self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result

    #--------------------------------------
    # unreachable
    #--------------------------------------
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
                    "type": "TASK ITEM - HOST UNREACHABLE", 
                    "host": str(result._host),
                    "name": str(result.task_name),
                    "contents": result._result,
                    "play": self.playname,
                    "task": self.taskname,
                }, 
                indent=4, 
                sort_keys=False,
            )

            if flush_results: 
                self._display.display(output)

            if log_results:
                self.write_log(output)

        elif default_json:
            host = result._host
            self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result


    #--------------------------------------
    # task skipped
    #--------------------------------------
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
                    "type": "TASK ITEM SKIPPED", 
                    "host": str(result._host),
                    "name": str(result.task_name),
                    "contents": result._result,
                    "play": self.playname,
                    "task": self.taskname,
                }, 
                indent=4, 
                sort_keys=False,
            )

            if flush_results: 
                self._display.display(output)

            if log_results:
                self.write_log(output)

        elif default_json:
            host = result._host
            self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result


    #--------------------------------------
    # end of all plays
    #--------------------------------------
    def v2_playbook_on_stats(self, stats):
        """Display info about playbook statistics"""

        self.end_time        =  datetime.now()
        self.end_time_str    =  self.end_time.strftime('%Y%m%d_%H%M%S')
        self.end_time_pretty =  self.end_time.strftime('%Y-%m-%d %H:%M:%S')

        self.job_length      =  self.start_time - self.end_time

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
                    "type": "ALL PLAYS DONE", 
                    "contents": {
                        'plays': self.results, # this may do nothing?
                        'stats': summary,
                        'end_time': self.end_time_pretty,
                        'job_length': str(self.job_length),
                    },
                }, 
                indent=4, 
                sort_keys=False,
            )

            if flush_results or default_json: 
                self._display.display(output)

            if log_results:
                self.write_log(output)

