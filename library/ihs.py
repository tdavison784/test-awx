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
module: ihs.py

short_description: Module to control IHS service state.

version_added: 1.0

description:
	- Control IHS service state

options:
  state:
    description:
      - started, stopped, restarted
      - will start, stop, or restart adminctl, or apachetcl service

  service:
    description:
      - adminctl, apachectl
      - adminctl is needed to communicate with WAS Dmgr cell
      - apachectl controls httpd process

author: Tommy Davison <tommy.davison@state.mn.us>
'''

EXAMPLES='''

- name: Start Admin Service
  ihs:
    state: started
    service: adminctl

- name: Restart HTTP Service
  ihs:
    state: restarted
    service: apachectl
'''

def ihs_run():

    module_args = dict(
        state=dict(type='str', required=True, choices=['restart', 'start', 'stop']),
        service=dict(type='str', required=True, choices=['adminctl', 'apachectl'])
    )

    module = AnsibleModule(
        argument_spec=module_args
    )

    state = module.params['state']
    service = module.params['service']

    #Set static vars
    http_root='/opt/WebSphere/HTTPServer'

    if state == 'start':
        if service == 'adminctl' and os.path.exists(http_root+'/logs/admin.pid'):
            module.exit_json(
                msg='adminctl is already running',
                changed=False
            )
        elif service == 'adminctl' and os.path.exists(http_root+'/logs/admin.pid') == False:
            child = sp.Popen(
                [
                    http_root+'/bin/adminctl start'
                ],
                shell=True,
                stdout = sp.PIPE,
                stderr = sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg='Failed to start adminctl process',
                    changed=False,
                    stderr = stderr_value,
                    stdout = stdout_value
                )
            module.exit_json(
                msg='Started adminctl process',
                changed=True
            )
        elif service == 'apachectl' and os.path.exists(http_root+'/logs/httpd.pid'):
            module.exit_json(
                msg='httpd process is already running',
                changed=False
            )
        elif service == 'apachectl' and os.path.exists(http_root+'/logs/httpd.pid') == False:
            child = sp.Popen(
                [
                    http_root+'/bin/apachectl start'
                ],
                shell=True,
                stdout = sp.PIPE,
                stderr = sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg='Failed to start apachectl process',
                    changed=False,
                    stderr = stderr_value,
                    stdout = stdout_value
                )
            module.exit_json(
                msg='Started apachectl process',
                changed=True
            )

    elif state == 'restart':
        child = sp.Popen(
            [
                http_root+'/bin/'+service+ ' restart'
            ],
            shell=True,
            stdout = sp.PIPE,
            stderr = sp.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        if child.returncode != 0:
            module.fail_json(
                msg='Failed to restart ' + service + ' process',
                changed=False,
                stderr = stderr_value,
                stdout = stdout_value
            )
        module.exit_json(
            msg='Restarted ' + service + ' process',
            changed=True
        )

    elif state == 'stop':
        if service == 'adminctl' and os.path.exists(http_root+'/logs/admin.pid') == False:
            module.exit_json(
                msg='adminctl process is not running',
                changed=False
            )
        elif service == 'adminctl' and os.path.exists(http_root+'/logs/admin.pid'):
            child = sp.Popen(
                [
                    http_root+'/bin/adminctl stop'
                ],
                shell=True,
                stdout = sp.PIPE,
                stderr = sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg='Failed to stop adminctl process',
                    changed=False,
                    stderr = stderr_value,
                    stdout = stdout_value
                )
            module.exit_json(
                msg='Stopped adminctl process',
                changed=True
            )
        elif service == 'apachectl' and os.path.exists(http_root+'/logs/httpd.pid') == False:
            module.exit_json(
                msg='apachectl process is not running',
                changed=False
            )
        elif service == 'apachectl' and os.path.exists(http_root+'/logs/httpd.pid'):
            child = sp.Popen(
                [
                    http_root+'/bin/apachectl stop'
                ],
                shell=True,
                stdout = sp.PIPE,
                stderr = sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg='Failed to stop apachectl process',
                    changed=False,
                    stderr = stderr_value,
                    stdout = stdout_value
                )
            module.exit_json(
                msg='Stopped apachectl process',
                changed=True
            )


def main():
    ihs_run()

if __name__ == '__main__':
    main()
