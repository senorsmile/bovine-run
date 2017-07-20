#!/usr/bin/env python

import json
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase

class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """
    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result

        This method could store the result in an instance attribute for retrieval later
        """
        host = result._host
        if 'stdout_lines' in result._result:
            output = {
                "task": str(result._task),
                "stdout_lines": result._result['stdout_lines'],
                #"full result": result._result,
            }
        if 'stdout' in result._result:
            output = {
                "task": str(result._task),
                "stdout": result._result['stdout'],
                #"full result": result._result,
            }
        elif 'msg' in result._result:
            output = { 
                "task": str(result._task),
                "msg": result._result['msg'],
                #"full result": result._result,
            }
        else:
            output = {
                "task": str(result._task),
                "full result": result._result,
            }

        final_output.append(
            {
                host.name: {
                    "output": output,
                },
            }, 
        )

        #print json.dumps(
        #    {
        #        host.name: {
        #            "output": output,
        #        },
        #    }, 
        #    indent=4,
        #)

final_output = []

Options = namedtuple(
    'Options', 
    [
        'connection',
        'module_path',
        'forks',
        'become',
        'become_method',
        'become_user',
        'check'
    ]
)

# initialize needed objects
variable_manager = VariableManager()
loader = DataLoader()
options = Options(
    connection='local',
    module_path='/path/to/mymodules',
    forks=100,
    become=None,
    become_method=None,
    become_user=None,
    check=False
)
passwords = dict(vault_pass='secret')

# Instantiate our ResultCallback for handling results as they come in
results_callback = ResultCallback()

# create inventory and pass to var manager
inventory = Inventory(
    loader=loader,
    variable_manager=variable_manager,
    host_list='localhost'
)
variable_manager.set_inventory(inventory)

# create play with tasks
play_source =  dict(
    name = "Ansible Play",
    hosts = 'localhost',
    gather_facts = 'no',
    tasks = [
        dict(
            action=dict(
                module='shell',
                args='ls'
            ),
            register='shell_out'
        ),
        dict(
            action=dict(
                module='pause',
                args=dict(
                    seconds=5,
                ),
            ),
        ),
        dict(
            action=dict(
                module='debug',
                args=dict(
                    msg='{{shell_out.stdout}}'
                ),
            ),
        ),
        dict(
            action=dict(
                module='command',
                args=dict(
                    args='exit 1'
                )
            ),
        ),
    ]
)

play = Play().load(
            play_source, 
            variable_manager=variable_manager, 
            loader=loader
        )

# actually run it
tqm = None
try:
    tqm = TaskQueueManager(
              inventory=inventory,
              variable_manager=variable_manager,
              loader=loader,
              options=options,
              passwords=passwords,
              # Use our custom callback instead of the ``default`` callback plugin
              stdout_callback=results_callback,
              run_additional_callbacks=False,
          )
    result = tqm.run(play)
finally:
    if tqm is not None:
        tqm.cleanup()

print(
    json.dumps(
        final_output,
        indent=4,
    )
)
