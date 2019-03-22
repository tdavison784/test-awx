#!/usr/bin/python
import os
import subprocess

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION='''
-
module: ibmim.py

short_description: Module to install IBM IM

version_added: 1.0

description:
	- Module to install IBM IM
	- Module assumes default installation directory 
	- Module skips over install if /eclipse/tools/imcl is present

options:

	state:

		description:
			- Determines whether or not to install or uninstall IBM IM
			- present will install
			- absent will uninstall

	src:

		description:
			- Local repo of IBM IM installation binaries

	dest:

		description:
			- Installation directory for IBM IM
			- Assumes path of /opt/WebSphere/InstallationManager

author: Tommy Davison (pwtwd35)
'''

EXAMPLES='''
---
-
  hosts: dev
  become: true
  become_method: sudo
  become_user: wsadmin
  tasks:
    -
      name: Install IBM IM using default path
      ibmim:
        src: /was855/IM188/
-------------------------
---
-
  hosts: dev
  become: true
  become_method: sudo
  become_user: wsadmin
  tasks:
    -
      name: Install IBM IM using non default path
      ibmim:
        src: /was855/IM188/
        dest: /opt/WebSphere/InstallationManager/
-------------------------
''' 

class IBM_IM_Installer():

	Module = None


	def __init__(self):
		"""Function to init all needed args"""
		self.module = AnsibleModule(
			argument_spec = dict(
				state = dict(required=True, choices=['present', 'absent']),
				src = dict(required=False),
				dest = dict(required=False, default='/opt/WebSphere/InstallationManager'),
			),
			supports_check_mode = True
		)

	def check_existence(self):
		result = os.path.exists(dest+"/eclipse/tools/imcl")
		if result:
			self.module.fail_json(
				msg="IBM IM is already installed",
				changed=False
			)

	def main(self):
		"""Function that will be doing all the work"""
		state = self.module.params['state']
		src = self.module.params['src']
		dest = self.module.params['dest']
	

		if state == 'present' and os.path.exists(dest+"/eclipse/tools/imcl") == False:

			child = subprocess.Popen(
				[src + "/userinstc "
				"-acceptLicense "
				"-installationDirectory " + dest],
				shell=True,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			)
			stdout_value, stderr_value = child.communicate()

			if child.returncode != 0:
				self.module.fail_json(
					msg="IBM IM failed to install",
					changed=False,
					stderr=stderr_value,
					stdout=stdout_value
				)
			self.module.exit_json(
					msg="IBM IM installed successfully",
					changed=True,
					stdout=stdout_value,
					stderr=stderr_value
			
			)
		else:
			self.module.exit_json(
				msg="IBM IM is already installed.",
				changed=False,
			)

		if state == 'absent':
			uninstall_dir = "/opt/WebSphere/InstallationManager/uninstall/uninstallc"
                        child = subprocess.Popen(
                                [uninstall_dir],
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE
                        )
                        stdout_value, stderr_value = child.communicate()

                        if child.returncode != 0:
                                self.module.fail_json(
                                        msg="IBM IM uninstall failed",
                                        stderr=stderr_value,
                                        stdout=stdout_value,
                                        module_facts=self.module_facts
                                )

                        self.module.exit_json(
                                changed=True,
                                msg="IBM IM successfully uninstalled",
                                stdout=stdout_value,
                                module_facts=self.module_facts
                        )


from ansible.module_utils.basic import *

if __name__ == "__main__":
	im = IBM_IM_Installer()
	im.main()
