# Copyright (C) 2017 Antoine Fourmy <antoine dot fourmy at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import OrderedDict, defaultdict
import warnings
try:
    from napalm_base import get_network_driver
except ImportError:
    warnings.warn('napalm not installed')
try:
    from jinja2 import Template
except ImportError:
    warnings.warn('jinja2 not installed')

napalm_actions = OrderedDict([
('ARP table', 'get_arp_table'),
('Interfaces counters', 'get_interfaces_counters'),
('Facts', 'get_facts'),
('Environment', 'get_environment'),
('Configuration', 'get_config'),
('Interfaces', 'get_interfaces'),
('Interface IP', 'get_interfaces_ip'),
('LLDP neighbors', 'get_lldp_neighbors'),
('LLDP neighbors detail', 'get_lldp_neighbors_detail'),
('MAC address', 'get_mac_address_table'),
('NTP servers', 'get_ntp_servers'),
('NTP statistics', 'get_ntp_stats'),
('Transceivers', 'get_optics'),
('SNMP', 'get_snmp_information'),
('Users', 'get_users'), # not implemented
('Network instances (VRF)', 'get_network_instances'), # not implemented
('NTP peers', 'get_ntp_peers'), # not implemented
('BGP configuration', 'get_bgp_config'), # not implemented
# ('Traceroute', 'traceroute'), # need argument
# ('BGP neighbors', 'get_bgp_neighbors'), # bug when no neighbors
# ('Routing table', 'get_route_to') # need argument
])

def open_device(credentials, node):
    driver = get_network_driver(node.operating_system.lower())
    device = driver(
                    hostname = credentials['ip_address'], 
                    username = credentials['username'], 
                    password = credentials['password'], 
                    optional_args = {'secret': credentials['enable_password']}
                    )
    device.open()
    return device

def napalm_update(device, node, update_allowed):
    for action, function in napalm_actions.items():
        if action in update_allowed:
            try:
                node.napalm_data[action] = getattr(device, function)()
            except NotImplementedError:
                node.napalm_data[action] = {}
    if 'Configuration' in update_allowed:
        node.napalm_data['Configuration']['compare'] = device.compare_config()
    if 'Logging' in update_allowed:
        node.napalm_data['cli'] = device.cli(['show logging'])

def standalone_napalm_update(credentials, update_allowed, *nodes):
    for node in nodes:
        device = open_device(credentials, node)
        napalm_update(device, node, update_allowed)
        device.close()
        
def napalm_commit(credentials, *nodes):
    for node in nodes:
        device = open_device(credentials, node)
        device.commit_config()
        napalm_update(device, node, {'Configuration'})
        device.close()
        
def napalm_discard(credentials, *nodes):
    for node in nodes:
        device = open_device(credentials, node)
        device.discard_config()
        napalm_update(device, node, {'Configuration'})
        device.close()
        
def napalm_load_merge(credentials, *nodes):
    for node in nodes:
        device = open_device(credentials, node)
        config = node.napalm_data['Configuration']['candidate']
        j2_config = Template(config).render(**node.__dict__)
        device.load_merge_candidate(config=j2_config)
        napalm_update(device, node, {'Configuration'})
        device.close()
        
def napalm_load_merge_commit(credentials, *nodes):
    for node in nodes:
        device = open_device(credentials, node)
        config = node.napalm_data['Configuration']['candidate']
        j2_config = Template(config).render(**node.__dict__)
        device.load_merge_candidate(config=j2_config)
        device.commit_config()
        napalm_update(device, node, {'Configuration'})
        device.close()
        
def napalm_load_replace(credentials, *nodes):
    for node in nodes:
        device = open_device(credentials, node)
        config = node.napalm_data['Configuration']['candidate']
        j2_config = Template(config).render(**node.__dict__)
        device.load_replace_candidate(config=j2_config)
        napalm_update(device, node, {'Configuration'})
        device.close()
        
def napalm_load_replace_commit(credentials, *nodes):
    for node in nodes:
        device = open_device(credentials, node)
        config = node.napalm_data['Configuration']['candidate']
        j2_config = Template(config).render(**node.__dict__)
        device.load_replace_candidate(config=j2_config)
        device.commit_config()
        napalm_update(device, node, {'Configuration'})
        device.close()
        
def napalm_rollback(credentials, *nodes):
    for node in nodes:
        device = open_device(credentials, node)
        device.rollback()
        napalm_update(device, node, {'Configuration'})
        device.close()
        
def napalm_ping(credentials, node, **parameters):
    device = open_device(credentials, node)
    result = device.ping(**parameters)
    device.close()
    return result
    
def napalm_traceroute(credentials, node, **parameters):
    device = open_device(credentials, node)
    result = device.traceroute(**parameters)
    device.close()
    return result
    
## pretty print the output

# this is a recursive function that pretty print the output based on what it contains.
# I keep track of how 'deep' the recursion goes to compute the appropriate amount
# of tabulation required
def str_dict(input, depth=0):
    tab = '\t'*depth
    if isinstance(input, list):
        result = '\n'
        for element in input:
            result += '{}- {}\n'.format(tab, str_dict(element, depth + 1))
        return result
    elif isinstance(input, dict):
        result = ''
        for key, value in input.items():
            result += '\n{}{}: {}'.format(tab, key, str_dict(value, depth + 1))
        return result
    else:
        return str(input)
        