#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import subprocess as sp

def get_gid():
    """Function to grep /etc/group on all server
    and report back if gid(s) exist on remote hosts
    """
    
    module_args=dict(
        message=dict(required=False)
    )
    module = AnsibleModule(
        argument_spec=module_args
    )

    gids = ['5010', '5009', '5008', '5007', '5006', '5005', '5004', '5002']

    for gid in gids:
        child = sp.Popen(
            [
                'grep ' + gid + ' /etc/group'
            ],
            shell=True,
            stdout=sp.PIPE,
            stderr=sp.PIPE
        )
        stdout_value, stderr_value = child.communicate()

        if stdout_value:
            print('The following groups exist on the servers ' + gid)
        else:
            print('The following groups do not exist on the servers '  + gid)


def main():
    get_gid()


if __name__ == '__main__':
    main()
               
