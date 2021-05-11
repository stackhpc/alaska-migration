from osutils.node import Node
import yaml
import jinja2

node = Node()

query = dict(
    name="name",
    instance_name="instance_info.display_name",
    resource_class="resource_class",
    device_serial="extra.system_vendor.serial_number",
)
ignore = set(
    [
        "doug",
        "openhpc-compute-0",
        "openhpc-compute-1",
        "openhpc-compute-2",
        "openhpc-compute-3",
        "openhpc-compute-4",
        "openhpc-compute-5",
        "openhpc-compute-6",
        "openhpc-compute-7",
        "openhpc-login-0",
        "openstack-hypervisor-1",
        "openstack-hypervisor-2",
        "openstack-hypervisor-3",
        "gpu-hypervisor-1",
        "ska-integration-if3lhiwdimgb-node-0",
        "ska-integration-if3lhiwdimgb-node-1",
        "ska-integration-if3lhiwdimgb-node-2",
        "storage-ssd-node-0",
        "storage-ssd-node-1",
        "vla22-test-dask",
    ]
)

import pandas as pd
df = pd.read_csv('devices.csv', index_col='old_device_name')

result = []
ignored = []
shortlist = []
deferred = []
for r in node.get_metadata(query=query):
    name = r["key"]
    prop = r["value"]
    i = prop["instance_name"]
    data = df.loc[name]
    assert data['device_serial'] == prop['device_serial']
    if i in ignore:
        ignored.append(i)
        deferred.append(name)
    else:
        result.append(r)
        shortlist.append(name)

print("Ignoring", sorted(ignored))
with open("result.yaml", "w") as fh:
    yaml.dump(sorted(result, key=lambda x: x["key"]), fh, indent=2)

def generate_inventory(nodes, name):
    template_str = """[baremetal-compute]
{% for n in nodes -%}
{{ n }} bmc_address={{ nodes[n].old_alaska_bmc_ip}} new_bmc_address={{ nodes[n].new_bmc_ip}} new_device_name={{ nodes[n].device_name }} device_serial={{ nodes[n].device_serial }}
{% endfor %}
"""
    env = jinja2.Environment()
    template = env.from_string(template_str)
    inventory = template.render(nodes=nodes)
    filename = f"inventory/{name}"
    with open(filename, "w") as f:
        f.write(inventory)
    print(f"Inventory written to: {filename}")

generate_inventory(df.loc[shortlist].T, "phase-1")
generate_inventory(df.loc[deferred].T, "phase-2")
