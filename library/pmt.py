#!/usr/bin/python

import subprocess as sp
from ansible.module_utils.basic import AnsibleModule
import datetime


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


DOCUMENTATION="""
---
module:  pmt.py

short_description:  IBM WAS Profile Managment Tool module

version_added: 2.0

description:  IBM WAS Profile Managment Tool module to run all things manageprofiles can do.

options:
    admin_passwd"
	    description:
		    - Type: String
			- Required: If profile_Root/soap.client.props username/password is not defined.
			  \ It is recommended to set the props file. 
			
	admin_user:
	    description:
		    - Type: String
		    - Required: If profile_Root/soap.client.props username/password is not defined.
			  \ It is recommended to set the props file
			
	
	augment:
	    description:
		    - Type: Boolean. If true, profile will augment. (WTX usage)
			- Required: False
	
	backup:
	    description:
		    - Type: Boolean. If true, the profile will backup.
			- Required: False
	
        dest:
	    description:
		    - Type: String
			- Required: False, only needed for backup and restore commands.
	
	dmgr_host:
	    description:
		    - Type: String
			- Required: False, only needed when federating node into dmgr cell.
	
	profile_name:
	    description:
		    - Type: String
			- Required: True, needed for all tasks.
			
	profile_root:
	    description:
		    - Type: String
			- Required: False, needed for backup, and restore,
			
	restore:
	    description:
		    - Type: Boolean
			- Required: False, needed for specifying profile restoration.
			
	state:
	    description:
		    - Type: String
			- Required: False, specify to create profile, or deleter.
			- Choices: present, absent, skip
	
	template_path:
	    description:
		    - Type: String
			- Required: False, specify path to profile properties file.
	
	unaugment:
	    description:
		    - Type: Boolean
			- Required: False, only needed if unaugmenting profile

author: Tommy Davison | <tommy.davison@state.mn.us>
"""


def pmt_run():
    module_args = dict(
        admin_user=dict(type='str', required=False),
        admin_passwd=dict(tpye='str', required=False, no_log=True),
        augment = dict(type='bool', required=False),
        backup = dict(tpye='bool', requried=False),
        dmgr_host = dict(type='str', required=False),
        profile_name = dict(type='str', required=True),
        profile_root = dict(type='str', required=False),
        restore = dict(type='bool', required=False),
        state = dict(type='str', required=False, choices=['absent', 'present', 'skip']),
        template_path = dict(type='str', required=False),
        unaugment = dict(type='str', required=False),
        was_root = dict(type='str', required=False)
    )


    module = AnsibleModule(
        argument_spec=module_args
    )

    admin_user = module.params['admin_user']
    admin_passwd = module.params['admin_passwd']
    augment = module.params['augment']
    backup = module.params['backup']
    dmgr_host = module.params['dmgr_host']
    profile_name = module.params['profile_name']
    profile_root = module.params['profile_root']
    restore = module.params['restore']
    state = module.params['state']
    template_path = module.params['template_path']
    unaugment = module.params['unaugment']
    was_root = module.params['was_root']

    #Set static vars
    date = datetime.datetime.now()
    date_format = date.strftime("%Y%m%d")

    if backup:
        child = sp.Popen(
            [
                profile_root + profile_name +'/bin/backupConfig.sh ' +
                '/tmp/'+profile_name+'Backup_'+date_format+'.zip ' +
                '-user ' + admin_user + ' -password ' +
                admin_passwd + ' -profileName ' + profile_name
            ],
            shell=True,
            stdout = sp.PIPE,
            stderr = sp.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        if child.returncode != 0:
            module.fail_json(
                msg='Failed to backup profile ' + profile_name,
                changed=False,
                stderr=stderr_value,
                stdout=stdout_value
            )
        module.exit_json(
            msg='Succesfully backed up profile ' + profile_name,
            changed=True
        )

    if restore:
        child = sp.Popen(
            [
                profile_root+'/bin/restoreConfig.sh' +
                ' /tmp/'+profile_name+'Backup_'+date_format+'.zip' +
                ' -user ' + admin_user + 
                ' -password ' + admin_passwd +
                ' -profileName ' + profile_name
            ],
            shell=True,
            stdout = sp.PIPE,
            stderr = sp.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        if child.returncode != 0:
            module.fail_json(
                msg='Failed to restore profile ' + profile_name,
                changed=False,
                stderr = stderr_value,
                stdout = stdout_value
            )
        module.exit_json(
            msg='Succesfully restored profile ' + profile_name,
            changed=True
        )

    if augment == True:
        child = sp.Popen(
            [
                was_root+'/bin/manageprofiles.sh -listAugments ' +
                '-profileName ' + profile_name
            ],
            shell=True,
            stdout = sp.PIPE,
            stderr = sp.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        profile_augments = stdout_value.splitlines()

        if len(profile_augments) < 3:
            child = sp.Popen(
                [
                    was_root +'/bin/manageprofiles.sh ' +
                    '-augment -profileName ' + profile_name +
                    ' -templatePath ' + was_root +'/profileTemplates/WTXAugment' +
                    ' -DTX_HOME_DIR /opt/wtx/tx4is'
                ],
                shell=True,
                stdout = sp.PIPE,
                stderr = sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg='Failed to augment profile ' + profile_name,
                    changed=False,
                    stderr=stderr_value,
                    stdout=stdout_value
                )
            module.exit_json(
                msg='Succesfully augmented profile ' + profile_name,
                changed=True
            )
        if len(profile_augments) >= 3:
            module.exit_json(
                msg='Profile ' + profile_name + ' is already augmented in this cell.',
                changed=False
            )

    if unaugment:
        child = sp.Popen(
            [
                was_root+'/bin/manageprofiles.sh -listAugments ' +
                '-profileName ' + profile_name
            ],
            shell=True,
            stdout = sp.PIPE,
            stderr = sp.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        profile_augments = stdout_value.splitlines()
        if len(profile_augments) < 3:
            module.exit_json(
                msg='Profile ' + profile_name + ' is not augmented in this cell.',
                changed=False
            )
        elif len(profile_augments) >= 3:
            child = sp.Popen(
                [
                    was_root+'/bin/manageprofiles.sh -unaugment ' +
                    '-profileName ' + profile_name + ' -templatePath ' + 
                    was_root +'/profileTemplates/WTXAugment'
                ],
                shell=True,
                stdout = sp.PIPE,
                stderr = sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg='Failed to unaugment profile ' + profile_name + ' from cell.',
                    changed=False,
                    stderr = stderr_value,
                    stdout = stdout_value
                )
            module.exit_json(
                msg='Succesfully unaugmented profile ' + profile_name + ' from cell.',
                changed=True
            )

    if state == 'present':
        child = sp.Popen(
            [
                was_root+'/bin/manageprofiles.sh -listProfiles'
            ],
            shell=True,
            stdout = sp.PIPE,
            stderr = sp.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        profiles = stdout_value
        if profile_name in profiles:
            module.exit_json(
                msg='Profile ' + profile_name + ' already exists in this cell.',
                changed=False
            )
        elif profile_name not in profiles and profile_name == 'Dmgr01':
            child = sp.Popen(
                [
                    was_root+'/bin/manageprofiles.sh -create' +
                    ' -templatePath ' +  
                    was_root +'/profileTemplates/management/' +
                    ' -adminUserName ' + admin_user +
                    ' -adminPassword ' + admin_passwd +
                    ' -enableAdminSecurity true' +
                    ' -profileRoot ' + profile_root +
                    ' -personalCertValidityPeriod 15' +
                    ' -serverType DEPLOYMENT_MANAGER' +
                    ' -signingCertValidityPeriod 20' +
                    ' -profileName ' + profile_name
                ],
                shell=True,
                stdout = sp.PIPE,
                stderr = sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg='Failed to create ' + profile_name,
                    changed=False,
                    stderr = stderr_value,
                    stdout = stdout_value
                )
            module.exit_json(
                msg='Succesfully created profile ' + profile_name,
                changed=True
            )
        elif profile_name not in profiles and profile_name == 'AppSrv01':
            child = sp.Popen(
                [
                    was_root +'/bin/manageprofiles.sh -create' +
                    ' -templatePath ' + 
                    was_root +'/profileTemplates/managed/' +
                    ' -dmgrAdminUserName ' + admin_user +
                    ' -dmgrAdminPassword ' + admin_passwd +
                    ' -profileRoot ' + profile_root +
                    ' -profileName ' + profile_name +
                    ' -dmgrHost ' + dmgr_host
                ],
                shell=True,
                stdout = sp.PIPE,
                stderr = sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg='Failed to create profile ' + profile_name,
                    changed=False,
                    stderr = stderr_value,
                    stdout = stdout_value
            )
            module.exit_json(
                msg='Succesfully created profile ' + profile_name,
                changed=True
            )
    if state == 'absent':
        child = sp.Popen(
            [
                was_root+'/bin/manageprofiles.sh -listProfiles'
            ],
            shell=True,
            stdout = sp.PIPE,
            stderr = sp.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        profiles = stdout_value
        if profile_name not in profiles:
            module.exit_json(
                msg='Profile ' + profile_name + ' does not exist in this cell',
                changed=False
            )
        elif profile_name in profiles:
            child = sp.Popen(
                [
                    was_root+'/bin/manageprofiles.sh -delete' +
                    ' -profileName ' + profile_name
                ],
                shell=True,
                stdout = sp.PIPE,
                stderr = sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg='Failed to delete profile  ' + profile_name + ' from cell.',
                    changed=False,
                    stderr = stderr_value,
                    stdout = stdout_value
                )
            module.exit_json(
                msg='Succesfully deleted ' + profile_name + ' from cell.',
                changed=True
            )

def main():
    pmt_run()

if __name__ == '__main__':
    main()
