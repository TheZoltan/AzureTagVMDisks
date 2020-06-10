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
        migrated_from = sys.argv[1]
        region = sys.argv[2]
        sub_id = sys.argv[3]
        client_id = sys.argv[4]
        secret = sys.argv[5]
        tenant = sys.argv[6]
    else:
        migrated_from = sys.argv[0]
        region = sys.argv[1]
        sub_id = sys.argv[2]
        client_id = sys.argv[3]
        secret = sys.argv[4]
        tenant = sys.argv[5]

    # Print cmdline vars
    print('Region:         ', region)
    print('sub_id:         ', sub_id)
    print('client_id:      ', client_id)
    print('secret:         ', secret)
    print('tenant:         ', tenant)





# Write to log
def updatelog(*argv):

    # Get current date/time
    curdt = datetime.now()
    curdt_str = curdt.strftime('[%d-%b-%Y %H:%M:%S.%f] ')

    # Update log
    log_line = ''
    logfile = open('azureimporttags.log', 'a+')
    logfile.writelines(curdt_str)
    for arg in argv:
        logfile.writelines(arg)

    logfile.writelines('\n')
    logfile.close()



# Iterate through all VMs....
def getallazvms(compute_client, az_vm_list):

    vm_list = compute_client.virtual_machines.list_all()

    i = 0
    for vm in vm_list:
        array = vm.id.split("/")
        resource_group = array[4]
        vm_name = array[-1]
        statuses = compute_client.virtual_machines.instance_view(resource_group, vm_name).statuses
        status = len(statuses) >= 2 and statuses[1]

        print(vm_name)

        az_vm_list.append(vm_name)


# Execute main function
if (__name__ == '__main__'):
    main()

