# check\_ib\_switch.py
This tool is used to monitor unmanaged Infiniband switches made by Mellanox. This script is using `mlxreg_ext` to query the register on the switches. The information could have errors since some guesswork is involved.

## Requirements
* `mgt`
* `python3`

## Usage
This script is intended to be used with NRPE. 

A switch can be accessed with its GUID or the combination of its name and the path to a node name map file.

The `--cable` option will also query each transciver to get their temperature. It will also display the cable information like its part number and length. 

```
usage: check_ib_switch.py [-h] [-v] [--guid GUID]
                          [--node_name_map NODE_NAME_MAP] [--name NAME]
                          [--fan] [--cable] [--psu] [--temp]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  --guid GUID           Switch GUID to check
  --node_name_map NODE_NAME_MAP
                        Node name map file path
  --name NAME           Switch name used in node-name-map
  --fan                 Check fans
  --cable               Check cables
  --psu                 Check PSUs
  --temp                Check temperatures
```

## Example
Serial numbers and switch name is redacted.

```
check_ib_switch.py --name switch0 --node_name_map /etc/node-name-map --psu --temp --fan --cable
Switch OK | PSU0_W=58;;30:100;; PSU1_W=65;;30:100;; Fan1_RPM=8493;;6000:10000;; Fan2_RPM=7232;;6000:10000;; Fan3_RPM=8389;;6000:10000;; Fan4_RPM=7119;;6000:10000;; Fan5_RPM=8389;;6000:10000;; Fan6_RPM=7156;;6000:10000;; Fan7_RPM=8441;;6000:10000;; Fan8_RPM=7232;;6000:10000;; Temperature1_C=22.4;;5:45;; Temperature2_C=31.2;;5:45;; Temperature3_C=25.6;;5:45;; Temperature4_C=30.4;;5:45;; Temperature5_C=27.2;;5:45;; Temperature6_C=32.8;;5:45;;
GUID=0xXXXXXXXXXXXXXXXX LID=31 Name=switch0
Scorpion2 IBEDRUnmanaged PN=057FVR Rev=A05 SN=XX
Cable #1, Mellanox PN=02F00T SN=XX Rev=E2 FW=0, 2M
Cable #2, Mellanox PN=MFA1A00-E030 SN=XX Rev=B1 FW=538837208, 30M
Cable #3, Mellanox PN=02F00T SN=XX Rev=E2 FW=0, 2M
Cable #4, Mellanox PN=MFA1A00-E030 SN=XX Rev=B1 FW=538837208, 30M
Cable #5, Mellanox PN=02F00T SN=XX Rev=E2 FW=0, 2M
Cable #6, Mellanox PN=MFA1A00-E030 SN=XX Rev=B1 FW=538837208, 30M
Cable #7, Mellanox PN=02F00T SN=XX Rev=E2 FW=0, 2M
Cable #8, Mellanox PN=0H4TJX SN=XX Rev=E2 FW=0, 3M
Cable #9, Mellanox PN=0684G2 SN=XX Rev=E3 FW=538837208, 10M
Cable #10, Mellanox PN=02F00T SN=XX Rev=E2 FW=0, 2M
Cable #11, Mellanox PN=0684G2 SN=XX Rev=E3 FW=538837208, 10M
Cable #12, Mellanox PN=02F00T SN=XX Rev=E2 FW=0, 2M
Cable #13, Mellanox PN=0684G2 SN=XX Rev=E3 FW=538837208, 10M
Cable #14, Mellanox PN=02F00T SN=XX Rev=E2 FW=0, 2M
Cable #15,  PN= SN= Rev= FW=0, 0M
Cable #16, Mellanox PN=02F00T SN=XX Rev=E2 FW=0, 2M
Cable #17,  PN= SN= Rev= FW=0, 0M
Cable #18, Mellanox PN=02F00T SN=XX Rev=E2 FW=0, 2M
Cable #19, Mellanox PN=MFA1A00-E030 SN=XX Rev=B1 FW=538837208, 30M
Cable #20, Mellanox PN=02F00T SN=XX Rev=E2 FW=0, 2M
Cable #21, Mellanox PN=MFA1A00-E030 SN=XX Rev=B1 FW=538837208, 30M
Cable #22, Mellanox PN=02F00T SN=XX Rev=E2 FW=0, 2M
Cable #23, Mellanox PN=MFA1A00-E030 SN=XX Rev=B1 FW=538837208, 30M
Cable #24, Mellanox PN=02F00T SN=XX Rev=E2 FW=0, 2M
Cable #25, Mellanox PN=0H4TJX SN=XX Rev=E2 FW=0, 3M
Cable #26, Mellanox PN=02F00T SN=XX Rev=E2 FW=0, 2M
Cable #27, Mellanox PN=0H4TJX SN=XX Rev=E2 FW=0, 3M
Cable #28, Mellanox PN=02F00T SN=XX Rev=E2 FW=0, 2M
Cable #29, Mellanox PN=0H4TJX SN=XX Rev=E2 FW=0, 3M
Cable #30, Mellanox PN=0684G2 SN=XX Rev=E3 FW=538837208, 10M
Cable #31, Mellanox PN=0H4TJX SN=XX Rev=E2 FW=0, 3M
Cable #32, Mellanox PN=0684G2 SN=XX Rev=E3 FW=538837208, 10M
Cable #33, Mellanox PN=02F00T SN=XX Rev=E2 FW=0, 2M
Cable #34, Mellanox PN=0684G2 SN=XX Rev=E3 FW=538837208, 10M
Cable #35, Mellanox PN=02F00T SN=XX Rev=E2 FW=0, 2M
Cable #36, Mellanox PN=0684G2 SN=XX Rev=E3 FW=538837208, 10M
```