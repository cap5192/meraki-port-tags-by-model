import meraki
import os
from dotenv import load_dotenv


# load all environment variables
load_dotenv()


def get_orgs():
    """Gets the list of all orgs (name and id) that admin has access to"""
    orgs = []
    dict = {"id": "", "name": ""}
    dashboard = meraki.DashboardAPI(api_key=os.environ['MERAKI_API_TOKEN'], output_log=False, print_console=False)
    response = dashboard.organizations.getOrganizations()

    for i in response:
        dict["id"] = i["id"]
        dict["name"] = i["name"]
        orgs.append(dict)
        dict = {"id": "", "name": ""}

    return orgs


def get_networks(org_id):
    """Get a list of networks and returns dict with net IDs and names"""
    nets = []
    dict = {"id": "", "name": ""}
    # collect network names
    dashboard = meraki.DashboardAPI(api_key=os.environ['MERAKI_API_TOKEN'], output_log=False, print_console=False)
    response = dashboard.organizations.getOrganizationNetworks(
        org_id, total_pages='all'
    )
    for i in response:
        dict["id"] = i["id"]
        dict["name"] = i["name"]
        nets.append(dict)
        dict = {"id": "", "name": ""}

    return nets

def get_network_switches(net_id):
    """Get network switches and returns a list of serial numbers and models in a dictionary"""
    switches = []
    dict = {"serial": "", "model": ""}
    dashboard = meraki.DashboardAPI(api_key=os.environ['MERAKI_API_TOKEN'], output_log=False, print_console=False)
    response = dashboard.networks.getNetworkDevices(
        net_id
    )
    for i in response:
        if i['model'][:2] == "MS":
            dict["serial"] = i["serial"]
            dict["model"] = i["model"]
            switches.append(dict)
            dict = {"serial": "", "model": ""}

    return switches


#apply update switch ports
def apply_port_tags(switches):
    """Updates port IDs with tags of its model number. If there is a tag present, it skips adding a tag"""
    dashboard = meraki.DashboardAPI(api_key=os.environ['MERAKI_API_TOKEN'], output_log=False, print_console=False)
    for i in switches:
        response = dashboard.switch.getDeviceSwitchPorts(i['serial'])
        for x in response:
            if i["model"] not in x['tags']:
                response = dashboard.switch.updateDeviceSwitchPort(
                    i["serial"], x['portId'],
                    tags=[i['model']]
                )
                print(f"Updating the tag on port ID {x['portId']} to {i['model']}")
            else:
                print("Port tags are already present, skipping...")
