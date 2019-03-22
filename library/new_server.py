#!/usr/bin/python
import subprocess as sp
from ansible.module_utils.basic import AnsibleModule


def run_server():

    module = AnsibleModule(
        argument_spec = dict(
            profile_name = dict(type='str', required=True),
            server_name = dict(type='list', required=True),
            state = dict(type='str', required=True),
            was_root = dict(type='str', required=True)
        )
    )

    profile_name = module.params['profile_name']
    server_name = module.params['server_name']
    state = module.params['state']
    was_root = module.params['was_root']

    if state == 'start':
        for server in server_name:
            child = sp.Popen(
                [
                    was_root + '/profiles/' + profile_name + '/bin/startServer.sh ' + server
                ],
                shell=True,
                stdout=sp.PIPE,
                stderr=sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()

            if child.returncode != 0:
                module.fail_json(
                    msg='Failed to start server ' + str(server_name),
                    changed=False,
	            stdout=stdout_value,
		    stderr=stderr_value
                )
            module.exit_json(
                msg='Succesfully started server ' + str(server_name),
                changed=True
            )

def main():
    run_server()


if __name__ == '__main__':
    main()
