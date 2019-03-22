#!/usr/bin/python

import os
from ansible.module_utils.basic import AnsibleModule


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: ibm_ihs

short_description: Module that controls the state of an IBM Deployment Manager

version_added: "4.0"

description:
    - Module that controls the state of IBM IHS Web Server.
    - Module control start and stop state for both adminctl and apachectl.
    - Support of dry run is provided with this module.

options:
    state:
        description:
            - Describes the state in which to send IBM IHS server.
        required: true
        choices:
          - start
          - stop
    path:
        description:
            - Path of IBM Install root. E.g /opt/IBM/WebSphere/HTTPServer
        required: true
        default:
          - /opt/IBM/WebSphere/HTTPServer
    name:
        description:
            - Name of the IHS service to start, stop, or restart.
        required: true
        choices:
          - adminctl
          - apachectl
author:
    - Tom Davison (@tntdavison784)
'''


EXAMPLES = '''
- name: Stop apachectl service
  ibm_ihs:
    state: stop
    path: /opt/IBM/WebSphere/HTTPServer
    name: apachectl
- name: Stop adminctl service
  ibm_ihs:
    state: stop
    path: /opt/IBM/WebSphere/HTTPServer
    name: adminctl
- name: Restart ihs all services
  ibm_ihs:
    state: restart
    path: /opt/IBM/WebSphere/HTTPServer
    name: "{{ item.service }}"
  loop:
    - { service: adminctl }
    - { service: apachectl }
'''


RETURN = '''
result:
    description: Descibes changed state or failed state
    type: str
message:
    description: Succesfully sent ihs into desired state.
'''


def send_service(module):
    """Function that will send adminctl or apachectl ihs
    service into desired state. Function is dynamic and not tied
    to any state so will run regardless of the state provided.
    There os lock file checks done in the main function to check service
    state."""


    service_cmd = """{0}/bin/{1} {2}""".format(module.params['path'],
                                                     module.params['name'],
                                                     module.params['state'])

    run_service = module.run_command(service_cmd)

    if run_service[0] != 0:
        module.fail_json(
            msg="Failed to send service {0} into state: {1}. See stdout/stderr for details.".format(module.params['name'],
                                                                                                    module.params['state']),
            changed=False,
            stdout=run_service[1],
            stderr=run_service[2]
        )

    module.exit_json(
        msg="Successfully sent service: {0} into state: {1}".format(module.params['name'],
                                                                    module.params['state']),
        changed=True
    )


def main():

    module = AnsibleModule(
            argument_spec=dict(
                state=dict(type='str',required=True, choices=['start','stop','restart']),
                name=dict(type='str',required=True, choices=['adminctl', 'apachectl']),
                path=dict(type='str',required=True, defaults='/opt/IBM/WebSphere/HTTPServer')
            ),
            supports_check_mode = True
    )

    state = module.params['state']
    name = module.params['name']
    path = module.params['path']


    admin_pid = "{0}/logs/admin.pid".format(path)
    httpd_pid = "{0}/logs/httpd.pid".format(path)

    if state =='start':
        if name == 'adminctl':
            if os.path.exists(admin_pid):
                module.exit_json(
                    msg="Service {0} is already running".format(name),
                    changed=False
                )
            send_service(module)
        if name == 'apachectl':
            if os.path.exists(httpd_pid):
                module.exit_json(
                    msg="Service {0} is already running".format(name),
                    changed=False
                )
            send_service(module)
    if state == 'stop':
        if name == 'adminctl':
            if not os.path.exists(admin_pid):
                module.exit_json(
                    msg="Service {0} is already stopped".format(name),
                    changed=False
                )
            send_service(module)
        if name == 'apachectl':
            if not os.path.exists(httpd_pid):
                module.exit_json(
                    msg="Service {0} is not running".format(name),
                    changed=False
                )
            send_service(module)
    if module.check_mode:
        if state == 'start':
            if name == 'adminctl':
                if os.path.exists(admin_pid):
                    module.exit_json(
                            msg="Service {0} is already running".format(name),
                            changed=False
                    )
                else:
                    module.exit_json(
                            msg="Service {0} will be sent into start state".format(name),
                            changed=True
                    )
            if name == 'apachectl':
                if os.path.exists(httpd_pid):
                    module.exit_json(
                            msg="Service {0} is already running ".format(name),
                            changed=False
                    )
                else:
                    module.exit_json(
                            msg="Service {0} will be sent into start state".format(name),
                            changed=True
                    )
        if state == 'stop': 
            if name == 'adminctl':
                if not os.path.exists(admin_pid):
                    module.exit_json(
                            msg="Service {0} is already stopped".format(name),
                            changed=False
                    )
                else:
                    module.exit_json(
                            msg="Service {0} will be sent into stop state".format(name),
                            changed=True
                    )
            if name == 'apachectl':
                if not os.path.exists(httpd_pid):
                    module.exit_json(
                            msg="Service {0} is already stopped".format(name),
                            changed=False
                    )
                else:
                    module.exit_json(
                            msg="Service {0} will be sent into stop state".format(name),
                            changed=True
                    )
        

if __name__ == '__main__':
    main()
