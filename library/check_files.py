#!/usr/bin/python

import fnmatch
import subprocess as sp
from ansible.module_utils.basic import AnsibleModule

def main():

    module=AnsibleModule(
        argument_spec=dict(
            error_code=dict(type='str', required=True),
            path=dict(type='str', required=True)
        )
    )

    path = module.params['path']
    error_code = module.params['error_code']
   
    t = sp.Popen(
        [
            'tail -2000 ' + path
            + ' > /tmp/Ansible-LogCheck-ForErrors.log'
        ],
        shell=True,
        stdout=sp.PIPE,
        stderr=sp.PIPE
    )
    t1 = sp.Popen(
        [
            'grep ' + error_code + ' /tmp/Ansible-LogCheck-ForErrors.log'
        ],
        shell=True,
        stdout=sp.PIPE,
        stderr=sp.PIPE
    )

    stdout_value, stderr_value = t1.communicate()
    if stdout_value:
        module.fail_json(msg='There is an error in ' + path, changed=False, stdout=stdout_value)
    module.exit_json(changed=False, msg='no errors to report') 
if __name__ == '__main__':
    main()

