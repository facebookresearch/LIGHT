#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.examine_utils import run_examine_or_review, print_results
from mephisto.data_model.worker import Worker

db = LocalMephistoDB()


def format_data_for_printing(data):
    nodes = data['data']['inputs']
    results = data['data']['outputs']['final_data']

    node_type = nodes['itemCategory']
    nodes = nodes['selection']
    node_map = {node['name']: 
        {
            'desc': node['description'], 
            'attributes': [a['name'] for a in node['attributes'] if a['value']],
        } for node in nodes
    }

    display_nodes = [
        f"{name}: {v['desc']}\n - attributes: [{', '.join(v['attributes'])}]"
        for name, v in node_map.items()
    ]
    print("\n".join(display_nodes))

    result_map = {n['name']: n['values']['custom'] + [k for k in n['values'].keys() if n['values'][k] and k != 'custom'] for n in results['nodes']}

    print(result_map)

    scale_attributes = results['attributes']
    custom_scale_attributes = scale_attributes['custom_attributes']
    del scale_attributes['custom_attributes']
    display_attributes = []
    for att_name, att_dict in scale_attributes.items():
        items = [(k, v) for k, v in att_dict.items()]
        if len(items) == 0:
            continue
        items.sort(key=lambda x: x[1])
        item_names = '\t'.join([i[0] for i in items])
        item_vals = '\t'.join([f"{i[1]:.3f}" for i in items])
        display_attributes.append(
            f"{att_name}:\n {item_names}\n{item_vals}"
        )
    for att_dict in custom_scale_attributes:
        items = [(k, v) for k, v in att_dict['vals'].items()]
        items.sort(key=lambda x: x[1])
        item_names = '\t'.join([i[0] for i in items])
        item_vals = '\t'.join([f"{i[1]:.3f}" for i in items])
        display_attributes.append(
            f"{att_dict['name']}: {att_dict['description']}\n {item_names}\n{item_vals}"
        )
    print("\n".join(display_attributes))

    worker_name = Worker.get(db, data["worker_id"]).worker_name
    contents = data["data"]
    duration = contents["times"]["task_end"] - contents["times"]["task_start"]
    metadata_string = (
        f"Worker: {worker_name}\nUnit: {data['unit_id']}\n"
        f"Duration: {int(duration)}\nStatus: {data['status']}\n"
    )

    inputs_string = ""
    outputs_string = ""

    if contents["inputs"] is not None and contents["outputs"] is not None:
        inputs = contents["inputs"]
        outputs = contents["outputs"]["final_data"]
        primary = outputs["primaryObject"]
        secondary = outputs["secondaryObject"]
        primary_object_map = {
            i["name"]: i["desc"] for i in inputs["primary_object_list"]
        }
        primary_object_stringlist = list(primary_object_map.keys())
        secondary_object_map = {
            i["name"]: i["desc"] for i in inputs["secondary_object_list"]
        }
        secondary_object_stringlist = list(secondary_object_map.keys())
        inputs_string = (
            f"Input:\n\tPrimary Object List: {primary_object_stringlist}\n"
            f"\tSecondary Object List: {secondary_object_stringlist}\n"
            f"\tSelected Context:\n"
            f"\t\t{primary}: {primary_object_map[primary]}\n"
            f"\t\t{secondary}: {secondary_object_map[secondary]}\n\n"
        )
        outputs_string = f"Output:\n\tUse {primary} with {secondary}\n\tAction: {outputs['actionDescription']}\n"

    return f"-------------------\n{metadata_string}{inputs_string}{outputs_string}"


def main():
    db = LocalMephistoDB()
    run_examine_or_review(db, format_data_for_printing)


if __name__ == '__main__':
    main()
