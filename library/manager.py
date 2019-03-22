#!/usr/bin/python
import subprocess as sp
from ansible.module_utils.basic import *



ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


DOCUMENTATION='''
---
module: server.py

short_description: Module that controls IBM Application server via JMX

version_added: "1.0"

description:
    - "Module that controls IBM Application server via JMX"
    - "The module itself doesn't control the JMX processes that is done on the CLI"
    - "The module invokes the CLI JMX calls"

options:
    profile_root:
        description:
            - The profile name of DMGR profile in WAS cell.
            - Required: True
            - Needed to specify the dmgr profile location


    state:
        description:
            - Determines the state of the deployment manager
            - Choices: ['start', 'stop']
            - Required: True


author: Tommy Davison <tommyboy784@gmail.com>

'''

EXAMPLES='''
- name: START DEPLOYMENT MANAGER
  manager:
    state: start
    profile_root: /opt/WebSphere/AppServer/profiles/Dmgr01

- name: STOP DEPLOYMENT MANAGER
  manager:
    state: stop
    profile_root: /opt/WebSphere/AppServer/profiles/Dmgr01
'''



def dmgr():
	""" Starts Dmgr WAS profile """

	module_args = dict(
		state = dict(type='str', required=True, choices=['start', 'stop']),
		profile_root = dict(type='str', required=True)
	)

	module = AnsibleModule(
		argument_spec = module_args
	)

	state = module.params['state']
	profile_root = module.params['profile_root']


	if state == 'start':
            child = sp.Popen(
                [
                    'find ' + profile_root+'/logs/dmgr/dmgr.pid',
                ],
                shell=True,
                stdout = sp.PIPE,
                stderr = sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if stdout_value:
                module.exit_json(
                    msg='Dmgr is already running',
                    changed=False
                )
            elif stdout_value == '':
                child = sp.Popen(
                    [profile_root+"/bin/startManager.sh"],
                    shell = True,
		    stdout = sp.PIPE,
		    stderr = sp.PIPE
		)
		stdout_value, stderr_value = child.communicate()
		if child.returncode != 0:
			module.fail_json(
				msg = "Failed to start Dmgr profile",
				changed = False,
				stderr = stderr_value,
				stdout = stdout_value
			)
		module.exit_json(
			msg = "Started Dmgr profile",
			changed = True
		)

	elif state == 'stop':
            child = sp.Popen(
                [
                    'find ' + profile_root+'/logs/dmgr/dmgr.pid',
                ],
                shell=True,
                stdout = sp.PIPE,
                stderr = sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if stdout_value == '':
                module.exit_json(
                    msg='Dmgr is already stopped',
                    changed=False
                )
            elif stdout_value:
	        child = sp.Popen(
		    [profile_root+"/bin/stopManager.sh"],
		    shell = True,
		    stdout = sp.PIPE,
		    stderr = sp.PIPE
		)
		stdout_value, stderr_value = child.communicate()

		if child.returncode != 0:
			module.fail_json(
				msg = "Failed to stop Dmgr profile",
				changed = False,
				stdout = stdout_value,
				stderr = stderr_value
			)
		module.exit_json(
			msg = "Stopped Dmgr",
			changed = True,
			stdout = stdout_value,
			stderr = stderr_value
		)


def main():
	dmgr()

if __name__ == "__main__":
	main()
