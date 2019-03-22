#!/usr/bin/python

import os
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: ibm_node

short_description: Module that controls the state of IBM Node Agent.

version_added: "2.1"

description:
    - Module that controls the state of IBM Node Agent.
    - Module is idempotent.
    - Module depends on having the pre-req IBM products installed.

options:
    state:
        description:
            - Describes the state in which to send IBM Node Agent.
        required: true
        choices: 
          - start
          - stop
    path:
        description:
            - Path of IBM Install root. E.g /opt/WebSphere/AppServer.
        required: true
    profile:
        description:
            - Name of IBM Profile that the node agent belongs to.
        required: true


author:
    - Tom Davison (@tntdavison784)
'''

EXAMPLES = '''
- name: Start Node Agent
  ibm_node:
    state: start
    path: /opt/WebSphere/AppServer
    profile: AppSrv01
- name: Stop Node Agent
  ibm_node:
    state: stop
    path: /opt/WebSphere/AppServer
    profile: AppSrv01
'''

RETURN = '''
result:
    description: Descibes changed state or failed state
    type: str
message:
    description: Succesfully put node agent into a state for profile

'''

def stop_node(module,state,path,profile):
    """Function that will stop IBM Node agent.
    Function is idempotent and will only stop if running.
    To determine running state, we will check for the default .pid
    location to determine state. Below are the return results:
    """

    if state == 'stop' and os.path.exists(path+'/profiles/'+profile+'/logs/nodeagent/nodeagent.pid'):
        stop_node =  module.run_command(path+'/profiles/'+profile+'/bin/stopNode.sh', use_unsafe_shell=True)

        if stop_node[0] != 0:
            module.fail_json(
                msg='Failed to send node agent into a %s state for profile %s' %(state, profile),
                changed=False,
                stderr=stop_node[2]
            )
        module.exit_json(
            msg='Succesfully sent node agent into a %s state for profile %s' %(state, profile),
            changed=True
        )
    else:
        module.exit_json(
            msg='Node Agent is not running.',
            changed=False
        )

def start_node(module,state,path,profile):
    """Function that will start Node Agent if stopped.
    Function is idempotent and will only start if stopped.
    To determine running state we will check for the default .pid
    location to determine state.
    """

    if not os.path.exists(path+'/profiles/'+profile+'/logs/nodeagent/nodeagent.pid'):
        start_node = module.run_command(path+'/profiles/'+profile+'/bin/startNode.sh', use_unsafe_shell=True)
        if start_node[0] != 0:
            module.fail_json(
                msg='Failed to send node agent into %s for profile %s' % (state, profile),
                changed=False,
                stderr=start_node[2]
            )
        module.exit_json(
            msg='Succesfully sent node agent into % state for profile %s' % (state, profile),
            changed=True
        )
    else:
        module.exit_json(
            msg='>>>>>>>> Node agent is already running <<<<<<<<'
        )

def main():
    """Main Function of the module.
    Function will import other modules into main body to run the main logic"""

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', required=True),
            path=dict(type='str', required=True),
            profile=dict(type='str', required=True)
        ),
        supports_check_mode = True
    )

    state = module.params['state']
    path = module.params['path']
    profile = module.params['profile']

    if state == 'stop' and not module.check_mode:
        stop_node(module,state,path,profile)

    if state == 'start' and not module.check_mode:
        start_node(module,state,path,profile)

    if module.check_mode:
        if state == 'stop':
            if os.path.exists("%s/profiles/%s/logs/nodeagent/nodeagent.pid"):
                module.exit_json(
                    msg="Sending Nodeagent into %s state" % (state),
                    changed=True
                )
            else:
                module.exit_json(
                    msg="NodeAgent is already in %s state" % (state),
                    changed=False
                )

        if state == 'start':
            if not os.path.exists("%s/profiles/%s/logs/nodeagent/nodeagent.pid"):
                module.exit_json(
                    msg="Sending node agent into %s state." % (state),
                    changed=True
                )
            else:
                module.exit_json(
                    msg="NodeAgent is already in %s state." % (state),
                    changed=False
                )

if __name__ == '__main__':
    main()
