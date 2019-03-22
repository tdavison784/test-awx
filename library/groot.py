#!/usr/bin/python


from ansible.module_utils.basic import AnsibleModule
import subprocess as sp


def greet_groot():
    """Function to have Groot greet you"""

    module_args=dict(
        message=dict(type='str', required=False)
    )

    module = AnsibleModule(
        argument_spec=module_args
    )


    message = module.params['message']

    command = module.run_command('cat i-am-groot',use_unsafe_shell=True)

    if command[0] != 0:
        module.fail_json(msg='Sorry, need groot permissions',changed=False)

    module.exit_json(
        changed=True,
        stdout=command[1]
    )


def main():
    greet_groot()

if __name__ == '__main__':
    main()
