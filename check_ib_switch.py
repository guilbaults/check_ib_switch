import re
import sys
import argparse
import logging
import subprocess
import itertools

def parse_table_hex(lines):
    info = {}
    for line in lines:
        m = re.match(r'(.*?)\s*\| (.*)', line)
        info[str(m.group(1))] = int(m.group(2), 16)
    return info

def parse_table_ascii(lines):
    info = {}
    for line in lines:
        m = re.match(r'(.*?)(\[\d+\])?\s*\| (.*)', line)
        field = str(m.group(1))
        value = str(bytearray.fromhex(m.group(3)[2:]).decode().replace(u'\x00', '').strip())
        if m.group(2):
            if field in info.keys():
                info[field] = info[field] + value
            else:
                info[field] = value
        else:
            info[field] = value
    return info

def mlxreg_ext_fans(lid, fan_id):
    cmdargs = ['mlxreg_ext', '-d', 'lid-{0}'.format(lid), '--reg_name', 'MFSM', '--get', '--indexes', 'tacho={}'.format(fan_id)]
    stdout, stderr = subprocess.Popen(cmdargs,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE).communicate()
    return parse_table_hex(stdout.decode("utf-8").splitlines()[4:-1])

def mlxreg_ext_temp(lid, sensor_id):
    cmdargs = ['mlxreg_ext', '-d', 'lid-{0}'.format(lid), '--reg_name', 'MTMP', '--get', '--indexes', 'sensor_index={}'.format(sensor_id)]
    stdout, stderr = subprocess.Popen(cmdargs,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE).communicate()
    return parse_table_hex(stdout.decode("utf-8").splitlines()[4:-1])

def mlxreg_ext_psu(lid):
    cmdargs = ['mlxreg_ext', '-d', 'lid-{0}'.format(lid), '--reg_name', 'MSPS', '--get']
    stdout, stderr = subprocess.Popen(cmdargs,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE).communicate()
    psus = {}
    lines = stdout.decode("utf-8").splitlines()[4:-1]
    for line in lines:
        # PSU Watt with 0x8 prependded
        m_watt = re.match(r'psu(\d)\[2\]\s+\| 0x8(.*)', line)
        if m_watt:
            psus['watt_' +m_watt.group(1)] = int(m_watt.group(2), 16)
    return psus

def mlxreg_ext(lid, register):
    cmdargs = ['mlxreg_ext', '-d', 'lid-{0}'.format(lid), '--reg_name', register, '--get']
    stdout, stderr = subprocess.Popen(cmdargs,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE).communicate()
    return parse_table_ascii(stdout.decode("utf-8").splitlines()[4:-1])

def ascii_field(name):
    for field in ['vendor_name', 'vendor_sn', 'vendor_pn', 'vendor_rev']:
        if field in name:
            return True
    return False

def mlxreg_ext_ports(lid, port_id):
    cmdargs = ['mlxreg_ext', '-d', 'lid-{0}'.format(lid), '--reg_name', 'PDDR', '--get', '--indexes', 'local_port={},pnat=0x0,page_select=0x3,group_opcode=0x0'.format(port_id)]
    stdout, stderr = subprocess.Popen(cmdargs,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE).communicate()
    lines = stdout.decode("utf-8").splitlines()[4:-1]
    info = parse_table_ascii(filter(ascii_field, lines))
    info.update(parse_table_hex(itertools.filterfalse(ascii_field, lines)))
    return info

def guid_to_lid():
    stdout, stderr = subprocess.Popen(['ibswitches'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE).communicate()
    lids = {} # store GUID to LID mapping
    for line in stdout.decode("utf-8").splitlines():
        logging.debug('guid_to_lid: %s', line)
        m = re.match(r'.*(0x.*) ports.* lid (\d+)', line)
        lids[m.group(1)] = int(m.group(2))
    return lids

def print_info(info):
    for item in info:
        print(item)

parser = argparse.ArgumentParser(description='')
parser.add_argument("-v", "--verbose", action="store_true",
                    help="increase output verbosity")
parser.add_argument("--guid", help="Switch GUID to check",
                    action="store")
parser.add_argument("--node_name_map", help="Node name map file path",
                    action="store")
parser.add_argument("--name", help="Switch name used in node-name-map",
                    action="store")
parser.add_argument("--fan", help="Check fans", action="store_true")
parser.add_argument("--cable", help="Check cables", action="store_true")
parser.add_argument("--psu", help="Check PSUs", action="store_true")
parser.add_argument("--temp", help="Check temperatures", action="store_true")

args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

if args.name == False and args.guid == False:
    print('Need to use the GUID or the switch name')
    sys.exit(3)

if args.name:
    if args.node_name_map == None:
        print('node_name_map need to be defined')
        sys.exit(3)

guid_name = {}
name_guid = {}
if args.node_name_map:
    with open(args.node_name_map) as f:
        for line in f:
            m = re.match(r'(0x.*) "(.*)"', line)
            if m:
                guid_name[m.group(1)] = m.group(2)
                name_guid[m.group(2)] = m.group(1)

guids = guid_to_lid()
if args.guid: 
    # received a GUID, check in node name map
    guid = args.guid
    if args.guid in guid_name:
        name = guid_name[args.guid]
    else:
        name = args.guid
else:
    # Received the name, need to get the GUID from the file
    guid = name_guid[args.name]
    name = args.name
lid = guids[guid]

perfdata = []
criticals = []
warnings = []
info = []

sw = mlxreg_ext(lid, 'MSGI')

info.append('GUID={} LID={} Name={}'.format(guid, lid, name))
info.append('{} PN={} Rev={} SN={}'.format(sw['product_name'], sw['part_number'], sw['revision'], sw['serial_number']))

if args.psu:
    psus = mlxreg_ext_psu(lid)
    for i in range(2):
        psu_watt = 'watt_{}'.format(i)
        if psus[psu_watt] < 30:
            criticals.append('PSU{0} is down with {}W'.format(i, psus[psu_watt]))
        if psus[psu_watt] > 100:
            warnings.append('PSU{0} might be alone with {}W'.format(i, psus[psu_watt]))
        perfdata.append('PSU{psu}_W={watt};;30:100;;'.format(
            psu=i,
            watt=psus[psu_watt],
        ))


if args.fan:
    for i in range(1,9):
        fan_info = mlxreg_ext_fans(lid, i)
        rpm = fan_info['rpm']
        if rpm < 6000:
            criticals.append('Fan #{} is too slow, {} RPM'.format(i, rpm))
        elif rpm > 10000:
            criticals.append('Fan #{} is too fast, {} RPM'.format(i, rpm))
        perfdata.append('Fan{fan}_RPM={speed};;{MIN_FAN}:{MAX_FAN};;'.format(
            fan=i,
            speed=rpm,
            MIN_FAN=6000,
            MAX_FAN=10000,
        ))

if args.temp:
    for i in range(1,7):
        temp_info = mlxreg_ext_temp(lid, i)
        temperature = temp_info['temperature']/10
        if temperature > 45:
            criticals.append('Temperature of #{} is too high, {}C'.format(i, temperature))
        perfdata.append('Temperature{sensor}_C={temp};;5:{MAX_TEMP};;'.format(
            sensor=i,
            temp=temperature,
            MAX_TEMP=45,
        ))
if args.cable:
    for i in range(1,37):
        cable = mlxreg_ext_ports(lid, i)
        temperature = cable['temperature']/256
        if temperature > 70:
            criticals.append('Cable {} is overtemp at {}C > 70C'.format(i, temperature))
        info.append('Cable #{}, {} PN={} SN={} Rev={} FW={}, {}M'.format(
            i,
            cable['vendor_name'],
            cable['vendor_pn'],
            cable['vendor_sn'],
            cable['vendor_rev'],
            cable['fw_version'],
            cable['cable_length'])
        )

if len(criticals) > 1:
    print('{criticals} | {perfdata}'.format(
        criticals=', '.join(criticals) + ', '.join(warnings),
        perfdata=' '.join(perfdata),
    ))
    print_info(info)
    sys.exit(2)
elif len(warnings) > 1:
    print('{warnings} | {perfdata}'.format(
        warnings=', '.join(warnings),
        perfdata=' '.join(perfdata),
    ))
    print_info(info)
    sys.exit(1)
else:
    print('Switch OK | {perfdata}'.format(
        perfdata=' '.join(perfdata),
    ))
    print_info(info)
    sys.exit(0)
