#!/usr/bin/python

import os
import subprocess as sp
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


DOCUMENTATION='''
---
module: node.py

short_description: Module that controls IBM Application server node agents

version_added: nodenoddin

description:
    - "Module that control the state of an IBM Application server node agent"
    - "The module itself doesn't control the JMX processes that is done on the CLI"
    - "The module invokes the CLI JMX calls"

options:
    profile_name:
        description:
            - The profile name of Custom profile in WAS cell.
            - Required: True
            - Needed to determine what profile the Application server belongs

    state:
        description:
            - Determines the state to send the Application server
            - Choices: ['start', 'stop']
            - Required: True

    was_root:
        description:
            - The current used WAS installation root. Ie. /opt/WebSphere/AppServer
            - Required: True

author: Tommy Davison <tommyboy784@gmail.com>

'''

EXAMPLES='''
- name: START NODE AGENT
  node:
    state: start
    profile_name: AppSrv01
    was_root: /opt/WebSphere/AppServer

- name: STOP NODE AGENT
  node:
    state: start
    profile_name: AppSrv01
    was_root: /opt/WebSphere/AppServer
'''



def node_agents():
    
    module_args=dict(
        profile_name=dict(type='str', required=True), 
        state=dict(type='str', required=True, choices=['stop', 'start', 'restart']),
        was_root=dict(type='str', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args
    )

    profile_name = module.params['profile_name']
    state = module.params['state']
    was_root = module.params['was_root']

    if state == 'start':
        if os.path.exists(was_root+'/profiles/'+profile_name+'/logs/nodeagent/nodeagent.pid'):
            module.exit_json(
                msg='Node Agent is already running for profile ' + profile_name,
                changed=False
            )
        elif os.path.exists(was_root+'/profiles/'+profile_name+'/logs/nodeagent/nodeagent.pid') == False:
            child = sp.Popen(
                [
                    was_root+'/profiles/'+profile_name+'/bin/startNode.sh'
                ],
                shell=True,
                stdout = sp.PIPE,
                stderr = sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg='Failed to start nodeagent for profile ' + profile_name,
                    changed=False,
                    stderr = stderr_value,
                    stout = stdout_value
                )
            module.exit_json(
                msg='Succesfully started nodeagent for profile ' + profile_name,
                changed=True
            )

    if state == 'stop':
        if os.path.exists(was_root+'/profiles/'+profile_name+'/logs/nodeagent/nodeagent.pid') == False:
            module.exit_json(
                msg='NodeAgent is not running for profile' + profile_name,
                changed=False
            )
        elif os.path.exists(was_root+'/profiles/'+profile_name+'/logs/nodeagent/nodeagent.pid'):
            child = sp.Popen(
                [
                    was_root+'/profiles/'+profile_name+'/bin/stopNode.sh'
                ],
                shell=True,
                stdout = sp.PIPE,
                stderr = sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg='Failed to stop nodeagent for profile ' + profile_name,
                    changed=False,
                    stderr = stderr_value,
                    stout = stdout_value
                )
            module.exit_json(
                msg='Succesfully stopped nodeagent for profile ' + profile_name,
                changed=True
            )

def main():
    node_agents()

if __name__ == '__main__':
    main()
