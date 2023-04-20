availabilityDomains = ["XJPz:AP-SINGAPORE-1-AD-1"]
displayName = 'Malima-SGVPS'
compartmentId = 'ocid1.tenancy.oc1..aaaaaaaaleh7tmge7oiqfxvxozolcggr6mothttvqmtdslggbkkxqjrw3aaq'
imageId = "ocid1.image.oc1.ap-singapore-1.aaaaaaaaabz5cp5zkrvmftn4t6uhaczxzyulwqlc3tpytl6ny7nwe7xknf6a"
subnetId = 'ocid1.subnet.oc1.ap-singapore-1.aaaaaaaawmomrv3k7q5slefx7exiujzegcox7eit4v5ozarqsinmak22httq'
ssh_authorized_keys = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCS41D5Apwqy+x48q5QwIkq6aA0u7Bbc5meSUoGpegBlqOnSdSF6kzbGtyX49sLXWE4kPYscslW2oLxuj0k+P+Cwdi7KdRxobC4X4Akim5KiQe6/I4NPNwkuf0ve6RV1JeSl5yS4D2R8CaR45DX/fdpMHr4EyXcDlY3z1XrzmwB5rflsywm0snylLtPudOHrIMUmDHY95OHHWSUIbSztlpaDMdcoi1pYlESqd6WBv1UfOJFZj3Iaa9RQUU/IR+4keI1207wBTcpSYphzKqwZN3lL0Fo/7Tk6+Xa80KXwlKobiVeV371w9CZrhriXPJggjZPLHy1aMy6sak/pzJnSOIP rsa-key-Madushan"

ocpus = 1
memory_in_gbs = 1
wait_s_for_retry = 10

import oci
import logging
import time
import sys
import requests

LOG_FORMAT = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler("oci.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logging.info("#####################################################")
logging.info("Script to spawn VM.Standard.E2.1.Micro instance")


message = f'Start spawning instance VM.Standard.E2.1.Micro - {ocpus} ocpus - {memory_in_gbs} GB'
logging.info(message)

logging.info("Loading OCI config")
config = oci.config.from_file(file_location="./config")

logging.info("Initialize service client with default config file")
to_launch_instance = oci.core.ComputeClient(config)

message = f"Instance to create: VM.Standard.E2.1.Micro - {ocpus} ocpus - {memory_in_gbs} GB"
logging.info(message)

logging.info("Check current instances in account")
current_instance = to_launch_instance.list_instances(compartment_id=compartmentId)
response = current_instance.data

total_ocpus = total_memory = _A1_Flex = 0
instance_names = []
if response:
    logging.info(f"{len	(response)} instance(s) found!")
    for instance in response:
        logging.info(f"{instance.display_name} - {instance.shape} - {int(instance.shape_config.ocpus)} ocpu(s) - {instance.shape_config.memory_in_gbs} GB(s) | State: {instance.lifecycle_state}")
        instance_names.append(instance.display_name)
        if instance.shape == "VM.Standard.E2.1.Micro" and instance.lifecycle_state not in ("TERMINATING", "TERMINATED"):
            _A1_Flex += 1
            total_ocpus += int(instance.shape_config.ocpus)
            total_memory += int(instance.shape_config.memory_in_gbs)

    message = f"Current: {_A1_Flex} active VM.Standard.E2.1.Micro instance(s) (including RUNNING OR STOPPED)"
    logging.info(message)
else:
    logging.info(f"No instance(s) found!")

message = f"Total ocpus: {total_ocpus} - Total memory: {total_memory} (GB) || Free {2-total_ocpus} ocpus - Free memory: {2-total_memory} (GB)"
logging.info(message)

if total_ocpus + ocpus > 2 or total_memory + memory_in_gbs > 2:
    message = "Total maximum resource exceed free tier limit (Over 2 AMD micro instances total). **SCRIPT STOPPED**"
    logging.critical(message)
    sys.exit()

if displayName in instance_names:
    message = f"Duplicate display name: >>>{displayName}<<< Change this! **SCRIPT STOPPED**"
    logging.critical(message)
    sys.exit()

message = f"Precheck pass! Create new instance VM.Standard.E2.1.Micro: {ocpus} opus - {memory_in_gbs} GB"
logging.info(message)

while True:
    for availabilityDomain in availabilityDomains:
        instance_detail = oci.core.models.LaunchInstanceDetails(
    metadata={
        "ssh_authorized_keys": ssh_authorized_keys
    },
    availability_domain=availabilityDomain,
    shape='VM.Standard.E2.1.Micro',
    compartment_id=compartmentId,
    display_name=displayName,
    source_details=oci.core.models.InstanceSourceViaImageDetails(
        source_type="image", image_id=imageId),
    create_vnic_details=oci.core.models.CreateVnicDetails(
        assign_public_ip=False, subnet_id=subnetId, assign_private_dns_record=True),
    agent_config=oci.core.models.LaunchInstanceAgentConfigDetails(
        is_monitoring_disabled=False,
        is_management_disabled=False,
        plugins_config=[oci.core.models.InstanceAgentPluginConfigDetails(
            name='Vulnerability Scanning', desired_state='DISABLED'), oci.core.models.InstanceAgentPluginConfigDetails(name='Compute Instance Monitoring', desired_state='ENABLED'), oci.core.models.InstanceAgentPluginConfigDetails(name='Bastion', desired_state='DISABLED')]
    ),
    defined_tags={},
    freeform_tags={},
    instance_options=oci.core.models.InstanceOptions(
        are_legacy_imds_endpoints_disabled=False),
    availability_config=oci.core.models.LaunchInstanceAvailabilityConfigDetails(
        recovery_action="RESTORE_INSTANCE"),
    shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
        ocpus=ocpus, memory_in_gbs=memory_in_gbs)
)
        try:
        	to_launch_instance.launch_instance(instance_detail)
        	message = 'VPS is created successfully! Watch video to get public ip address for your VPS'
        	logging.info(message)
        	sys.exit()
        except oci.exceptions.ServiceError as e:
            if e.status == 500:
            	message = f"{e.message} Retry in {wait_s_for_retry}s"
            else:
            	message = f"{e} Retry in {wait_s_for_retry}s"
            logging.info(message)
            time.sleep(wait_s_for_retry)
        except Exception as e:
        	message = f"{e} Retry in {wait_s_for_retry}s"
        	logging.info(message)
        	time.sleep(wait_s_for_retry)
        except KeyboardInterrupt:
        	sys.exit()