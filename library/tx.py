#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION='''
---
module:  tx.py

short_description:  Module to install tx client silently

version_added: 1.0

description:  IBM TX installation. Module to install TX silently.

options:
    response_file:
        description:
            - Type: String.
            - Required: False.

    state:
        description:
            - Type: String.
            - Required: False.
            - Choices: absent, present

author: Tommy Davison | <tommy.davison@state.mn.us>
'''
import subprocess as sp
import os
from ansible.module_utils.basic import AnsibleModule

def install_tx():
	"""Module to set all arguments
	   And the logic that will execute
	   During module runtime """

	module_args = dict(
		response_loc = dict(type='str', required=False),
		state = dict(type='str', required=False, choices=['absent', 'present'])
	)

	module = AnsibleModule(
		argument_spec = module_args
	)

	response_loc = module.params['response_loc']
	state = module.params['state']

	dtxinfo = '/opt/wtx/tx4is/bin/dtxinfo'


        if state == 'absent':
		child = sp.Popen(
			['/opt/wtx/tx4is/dtx_install/IBM_WebSphere_Transformation_Extender_for_Integration_Servers.uninstall'],
			shell = True,
			stdout = sp.PIPE,
			stderr = sp.PIPE
		)
		stdout_value, stderr_value = child.communicate()

		if child.returncode != 0:
			module.fail_json(
				msg = "Failed to uninstall TX...",
				changed = False,
				stderr = stderr_value,
				stdout = stdout_value
			)
		module.exit_json(
			msg = "Succesfully uninstalled TX...",
			changed = True
		)

	elif os.path.exists(dtxinfo) == False and state == 'present':
		child = sp.Popen(
			['/was855/ITX_INTEG_SVRS_V9.0_LINUX_X86_ML/9.0.0.2-ITX-wsdtxis-linux/DTXINST -s' +
			response_loc + ' -I /opt/wtx/temp/install_TX.log ' +
                        '&& /opt/wtx/tx4is/OSGi/deploy/wtxDeployOSGi.sh /opt/IBM/ProcessServer'
                        ],
			shell = True,
			stdout = sp.PIPE,
			stderr = sp.PIPE
		)
		stdout_value, stderr_value = child.communicate()

                if child.returncode != 0:
			module.fail_json(
				msg = "Failed to install TX... Check /opt/wtx/temp/install_TX.log for details",
				changed = False,
				stderr = stderr_value,
				stdout = stdout_value
			)

		module.exit_json(
			msg = "Succesfully installed TX and deployed WTX OSGI",
			changed = True
		)
		module.fail_json(
		    msg = "Failed to deploy WTX OSGI...",
		    changed = False,
		    stderr = stderr_value,
		    stdout = stdout_value
                )
	else:
		module.exit_json(
			msg = "TX not installed on server",
			changed = False
		)


def main():
	install_tx()

if __name__ == "__main__":
	main()
