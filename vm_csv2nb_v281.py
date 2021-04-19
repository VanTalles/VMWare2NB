import csv
import pandas
import pynetbox

file_path = "xxx.csv"

nb = pynetbox.api('https://net_box',token = 'xxx')
nb.http_session.verify = False

TENANT = .. # The Tenant ID
SITE = .. # The Site ID

vm_list = []

nb_item = []

conv_base = dict(MB = 1,GB = 1024,TB = 1048576)
conv_base2 = dict(MB = 0.000976, GB = 1, TB = 1024)

def convertMGT(str1):
    ret = 0
    if str1:
        rt = str1.strip().split()
        ret = float(rt[0])*conv_base.get(rt[1])
    return ret

def convertMGT2(str1):
    ret = 0
    if str1:
        rt = str1.strip().split()
        ret = float(rt[0])*conv_base2.get(rt[1])
    return ret

def state(str1):
    ret = 'offline'
    if str1 == 'Powered On':
        ret = 'active'
    return ret

def make_nb_item(row):
    vm_list.append(row)
    item = {'host':{
#        'role' : '',
        'cluster' : 23,
        'tenant' : TENANT,
        'name' : (row['Name']),
        'disk' : int(convertMGT2(row['Provisioned Space'])),
        'memory' : int(convertMGT(row['Memory Size'])),
        'vcpus' : int(row['CPUs']),
        'status' : state(row['State'])
    }, 'ip' : row['IP Address'].split(',')[0]}
    nb_item.append(item)

with open(file_path, 'r', encoding = 'utf-8-sig') as f:
    reader = csv.DictReader(f, delimiter = ',')
    for row in reader:
        make_nb_item(row)


for it1 in nb_item:

    vm_new = nb.virtualization.virtual_machines.create(it1['host'])
    item_interface = dict (
        virtual_machine = vm_new.id,
        name = "Ethernet0",
        type = 'virtual',
    )
    vm_int_new = nb.virtualization.interfaces.create(item_interface)
    if it1['ip']:
        item_ip = dict (
            family = 4,
            address = it1["ip"]+'/24',
            tenant = TENANT,
            status = 'active',
            interface = vm_int_new.id,
 #           assigned_object_type = 'dcim.interface',
        )
        iip = nb.ipam.ip_addresses.create(item_ip)
        vm_new.primary_ip4 = iip
    vm_new.save()
