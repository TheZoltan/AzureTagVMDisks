import sys
import os
import json
from datetime import datetime
from azure.mgmt.resource import SubscriptionClient
import azure.common.credentials as creds
from azure.common.credentials import ServicePrincipalCredentials
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.resource import ResourceManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption
from msrestazure.azure_exceptions import CloudError


def main():
    pass
    print('AzureTagVMDisks v1.0')


    # Check that we have args
    if (len(sys.argv) < 7):
        print('YOU MUST SPECIFY THE CORRECT COMMAND LINE PARAMETERS:')
        print('Usage:')
        print('azureimporttags.py [migrated_from] [azure_region] [subscriptiom] [client_id] [secret] [tenant]')
        print('NOTE: the migrated_from field should contain one of these values:')
        print('  On Premise')
        print('  AWS')
        print('  Azure')
        print('  Equinix')
        print('  CGI')
        print('')
        sys.exit(1)


   # Get command line args
    if (sys.argv[0] == 'python'):
        migrated_from = sys.argv[2]
        region = sys.argv[3]
        sub_id = sys.argv[4]
        client_id = sys.argv[5]
        secret = sys.argv[6]
        tenant = sys.argv[7]
    else:
        migrated_from = sys.argv[1]
        region = sys.argv[2]
        sub_id = sys.argv[3]
        client_id = sys.argv[4]
        secret = sys.argv[5]
        tenant = sys.argv[6]

    # Print cmdline vars
    print('Migrated from:  ', migrated_from)
    print('Region:         ', region)
    print('sub_id:         ', sub_id)
    print('client_id:      ', client_id)
    print('secret:         ', secret)
    print('tenant:         ', tenant)



    # Begin logging
    updatelog('----- Logging Started -----')

   # If not a valid migrated_from field, abort with error
    migrated_from_cases = {
        'On Premise': 'On Premise',
        'AWS': 'AWS',
        'Azure': 'Azure',
        'Equinix': 'Equinix',
        'CGI': 'CGI',
        'Native': 'Native'
    }
    migrated_from = migrated_from_cases.get(migrated_from, 'INVALID')
    if (migrated_from == 'INVALID'):
        print('')
        print('ERROR: invalid migrated_from arg was passed')
        updatelog('ERROR: invalid migrated_from arg was passed: ', migrated_from)
        print('')
        exit(2)

    print('migrated_from: ', migrated_from)
    updatelog('migrated_from: ', migrated_from)

    # Get creds
    updatelog('Calling ServicePrincipalCredentials()')
    subscription_id = sub_id
    #credentials = ServicePrincipalCredentials(client_id = client_id, secret = secret, tenant = tenant)

    # Testing this code
    credentials = creds.get_azure_cli_credentials(resource=None, with_tenant=False)[0]
    sub_client = SubscriptionClient(credentials)

    # Create object for compute-related interactions
    updatelog('Calling ComputeManagementClient()')
    compute_client = ComputeManagementClient(credentials, subscription_id)

    # Get all Azure VMs
    updatelog('Calling getallazvms()')

    # Get list of all resource groups
    rg_list = []
    getresourcegrplist(credentials, subscription_id, rg_list)

    getvmdisks(compute_client, rg_list, migrated_from)


    updatelog('----- Exiting -----')


# Get list of resource groups
def getresourcegrplist(credentials, subscription_id, rg_list):

    client = ResourceManagementClient(credentials, subscription_id)

    for item in client.resource_groups.list():
        rg_list.append(item.name)
        #print('RG: ', item.name)


# Write to log
def updatelog(*argv):

    # Get current date/time
    curdt = datetime.now()
    curdt_str = curdt.strftime('[%d-%b-%Y %H:%M:%S.%f] ')

    # Update log
    log_line = ''
    logfile = open('azureTagVMDisks.log', 'a+')
    logfile.writelines(curdt_str)
    for arg in argv:
        logfile.writelines(arg)

    logfile.writelines('\n')
    logfile.close()


# Get disks from each VM
def getvmdisks(compute_client, rg_list, migrated_from):


    print('In getvmdisks()')


    # This will list all disks in a RG

    for resource_grp in rg_list:

        disks = compute_client.disks.list_by_resource_group(resource_grp)
        for disk in disks:
            #print('Disk: ', disk)
            #print('Managed By: ', disk.managed_by)
            #print('Id: ', disk.id)

            # Parse out VM name
            vm_name = disk.managed_by.rsplit('/', 1)[1]
            print('vmname: ', vm_name)
            updatelog('VMName: ', vm_name, 'Disk: ', disk.name)

            disk.tags = {'Name':vm_name, 'Migrated From': migrated_from}
            updatelog('Tags: Name:', vm_name, ' Migrated From:', migrated_from)
            compute_client.disks.create_or_update(resource_grp, disk.name, disk)



# Iterate through all VMs....
def getallazvms(compute_client, az_vm_dict):

    vm_list = compute_client.virtual_machines.list_all()

    i = 0
    for vm in vm_list:
        array = vm.id.split("/")
        resource_group = array[4]
        vm_name = array[-1]
        statuses = compute_client.virtual_machines.instance_view(resource_group, vm_name).statuses
        status = len(statuses) >= 2 and statuses[1]

        print('Name: ', vm_name, 'Resource Grp: ', resource_group)

        az_vm_dict[vm_name] = resource_group


# Execute main function
if (__name__ == '__main__'):
    main()

