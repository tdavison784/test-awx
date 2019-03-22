#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import subprocess as sp
import shutil


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION='''
---

module: cleanup.py

short_description: Module to run regular IBM Application server cleanup steps

version_added: 1.0

description:
    - Module to run regular IBM Application server cleanup steps.
    - Module has many saftey checks to ensure that no harm can be done to fs
    - For this reason, was_root was forced to have choices, so that a user could not specify "/" or "/var" or "/var/messages", etc..
    - Module will check for any running IBM Java processes before attempting cleanup
    - If module detects running processes it will fail
    - Module cleanups the following dirs: <WAS_Profile_Root>/temp, /wstemp, /workspace
    - After dir is cleaned, then will clear classCache, and osgiCfgInit cache
    - Module will catch itsel and not clear cache if cleanup dirs are not present

options:
    profile_name:
      description:
        - Type: string
        - Required: True
        - Name of IBM Profile to cleanup    

    was_root:
      description:
        - Type: string
        - Required: True
        - Location of IBM install directory

author: Tommy Davison <tommyboy784@gmail.com>
'''

EXAMPLES='''
---
-
  name: Run WAS cleanup
  cleanup:
    profile_name: AppSrv01
    was_root: /opt/WebSphere/AppServer
'''


def run_cleanup():
    """Function to run general cleanup of IBM Application server
	Function will do the following saftey checks
	1. Check to see if any running JAVA processes exist
	if .pid files exist in <WAS_Profile_Root>/logs dir
	then changed=False and will print message to ensure
	all java processes are stopped before running cleanup
    """
	
    module_args=dict(
	profile_name=dict(type='str', required=True),
	was_root=dict(type='str', required=True, choices=['/opt/WebSphere/AppServer', 
        '/opt/WebSphere85/AppServer', '/opt/WebSphere/AppServer8.5.5', '/opt/IBM/WebSphere/AppServer',
        '/opt/IBM/ProcessServer'])
    )
	
    module = AnsibleModule(
	argument_spec=module_args
    )

    profile_name = module.params['profile_name']
    was_root = module.params['was_root']
    
    cleanup_dirs = ['/wstemp', '/temp', '/workspace']
    cache = ['clearClassCache.sh', 'osgiCfgInit.sh -all']

    child = sp.Popen(
        [
            'find ' + was_root + '/profiles/' + profile_name +
            '/logs/ -name *.pid'
	],
	shell=True,
	stdout=sp.PIPE,
	stderr=sp.PIPE
    ) 
    stdout_value, stderr_value = child.communicate()

    if stdout_value:
        module.fail_json(
            msg="Won't run cleanup as java processes are still running... please stop them then try again",
            changed=False,
	    stdout=stdout_value
	)
    else:
        try:

            for dirs in cleanup_dirs:
                shutil.rmtree(was_root+'/profiles/'+profile_name+dirs)
        except OSError:
            module.exit_json(
                msg='Cleanup dirs have already been deleted',
                changed=False
            ) 
        else:
            child = sp.Popen(
                [
                    was_root + '/profiles/' + profile_name + '/bin/' + cache[0]
                ],
                shell=True,
                stdout=sp.PIPE,
                stderr=sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg='Something went wrong and failed to clean all class cache',
                    changed=False,
                    stderr=stderr_value,
                    stdout=stdout_value
                )
            else:
                child = sp.Popen(
                    [
                        was_root + '/profiles/' + profile_name + '/bin/' + cache[1]
                    ],
                    shell=True,
                    stdout=sp.PIPE,
                    stderr=sp.PIPE
                )
                stdout_value, stderr_value = child.communicate()
                if child.returncode != 0:
                    module.fail_json(
                        msg='Failed to clear osgi cache',
                        changed=False,
                        stderr=stderr_value,
                        stdout=stdout_value
                    )
                module.exit_json(
                    msg='Successfully cleared class cache and osgi cache',
                    changed=True
                )


def main():
    run_cleanup()
	
if __name__ == '__main__':
    main()
