#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import subprocess as sp
import os


TODO='''
List of TODO items for this module:
1. Change server_name type from str => list
2. Look into multi-process Server starts, or nowait option added
'''

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


DOCUMENTATION='''
---
module: server.py

short_description: Module that controls IBM Application server via JMX

version_added: "cheeta"

description:
    - "Module that controls IBM Application server via JMX"
    - "The module itself doesn't control the JMX processes that is done on the CLI"
    - "The module invokes the CLI JMX calls"

options:
    profile_name:
        description:
            - The profile name of Custom profile in WAS cell.
            - Required: True
            - Needed to determine what profile the Application server belongs to

    server_name:
        description:
            - Name of server in WAS cell to be started, stopped, or have status check
            - Required: True

    state:
        description:
            - Determines the state to send the Application server
            - Choices: ['check', 'start', 'stop']
            - Required: True

    was_root:
        description:
            - The current used WAS installation root. Ie. /opt/WebSphere/AppServer
            - Required: True

    nowait:
        description:
            - Tells the JMX call not to wait for initilization.
            - Return control to prompt
            - Required: False

author: Tommy Davison <tommyboy784@gmail.com>

'''

EXAMPLES='''
#start server
---
-
  name: START SERVER
  server:
    state: start
    profile_name: AppSrv01
    server_name: Server01
    was_root: /opt/WebSphere/AppServer


---
-
  name: START SERVER
  server:
    state: start
    profile_name: AppSrv01
    server_name: Server01
    was_root: /opt/WebSphere/AppServer
    nowait: True


#stop server
---
-
  name: STOP SERVER
  server:
    state: stop
    profile_name: AppSrv01
    server_name: Server01
    was_root: /opt/WebSphere/AppServer

#check server status
---
-
  name: STOP SERVER
  server:
    state: check
    profile_name: AppSrv01
    server_name: Server01
    was_root: /opt/WebSphere/AppServer

'''


def run_server():
    """Function that will control all JMX IBM Application server calls
    Function will stop, start and check server status
    """

    module_args=dict(
        profile_name=dict(type='str', required=True),
        state=dict(type='str', required=True, choices=['check', 'start', 'stop']),
        server_name=dict(type='str', required=True),
        was_root=dict(type='str', required=True),
        nowait=dict(type='bool', required=False)
    )

    module = AnsibleModule(
        argument_spec=module_args
    )

    profile_name = module.params['profile_name']
    state = module.params['state']
    server_name = module.params['server_name']
    was_root = module.params['was_root']
    nowait = module.params['nowait']


    if state == 'start':
        if os.path.exists(was_root + '/profiles/' + profile_name +
        '/logs/' + server_name + '/' + server_name + '.pid'):
            module.exit_json(
                msg='Server is already running',
                changed=False
            )
        elif state == 'start':
            child = sp.Popen(
                [
                    was_root + '/profiles/' + profile_name +
                    '/bin/startServer.sh ' + server_name 
                ],
                shell=True,
                stdout=sp.PIPE,
                stderr=sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()


            if child.returncode != 0:
                module.fail_json(
                    msg='Failed to start server. See log for details ---> ' +
                    was_root + '/profiles/' + profile_name + '/logs/' + server_name +
                    '/startServer.log',
                    changed=False
                )
            module.exit_json(
                msg='Succesfully started server ' + server_name,
                changed=True
            )

    if state == 'stop':
        if os.path.exists(was_root + '/profiles/' + profile_name +
        '/logs/' + server_name + '/' + server_name + '.pid') == False:
            module.exit_json(
                msg='Server is not started ' + server_name,
                changed=False
            )
        else:
            child =  sp.Popen(
                [
                    was_root + '/profiles/' +  profile_name +
                    '/bin/stopServer.sh ' + server_name 
                ],
                shell=True,
                stdout=sp.PIPE,
                stderr=sp.PIPE
            )
            stdout_value, stderr_value =  child.communicate()

            if child.returncode != 0:
                module.fail_json(
                    msg='Failed to stop server. See log for details ---> ' + 
                    was_root + '/profiles/' + profile_name + '/logs/' + server_name +
                    '/stopServer.log',
                     changed=False,
                 )
            module.exit_json(
                msg='Succesfully stopped server ' + server_name,
                changed=True
             )

    if state == 'check':
        child = sp.Popen(
            [
                was_root + '/profiles/' + profile_name +
                '/bin/serverStatus.sh ' + server_name
            ],
            shell=True,
            stdout=sp.PIPE,
            stderr=sp.PIPE
        )
        stdout_value, stderr_value = child.communicate()

        if child.returncode != 0:
            module.fail_json(
                msg='Failed to check server status. See log for details ---> ' +
                was_root + '/profiles/' + profile_name + '/logs/' + server_name +
                '/serverStatus.log',
                changed=False
            )
        module.exit_json(
            changed=False,
            stdout =  stdout_value,
            stderr =  stderr_value
        )

def main():
    run_server()

if __name__ == '__main__':
    main()
