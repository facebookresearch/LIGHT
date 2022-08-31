# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.examine_utils import run_examine_or_review, print_results
from mephisto.data_model.worker import Worker
from light.colors import Colors as C

db = LocalMephistoDB()


def format_data_for_printing(data):
    nodes = data["data"]["inputs"]
    results = data["data"]["outputs"]["final_data"]

    node_type = nodes["itemCategory"]
    nodes = nodes["selection"]
    node_map = {
        node["name"]: {
            "desc": node["description"],
            "attributes": [a["name"] for a in node["attributes"] if a["value"]],
        }
        for node in nodes
    }

    result_map = {
        n["name"]: n["values"]["custom"]
        + [k for k in n["values"].keys() if n["values"][k] and k != "custom"]
        for n in results["nodes"]
    }

    def make_colored_attributes(old_list, new_list):
        atts = []
        for att in old_list:
            if att in new_list:
                atts.append(att)
            else:
                atts.append(f"{C.BOLD_RED}{att}{C.RESET}")
        for att in new_list:
            if att not in old_list:
                atts.append(f"{C.BOLD_GREEN}{att}{C.RESET}")
        return ", ".join(atts)

    display_nodes = [
        f"{C.BOLD_BLUE}{name}{C.RESET}: {v['desc']}\n - attributes: [{make_colored_attributes(v['attributes'], result_map[name])}]"
        for name, v in node_map.items()
    ]
    attributes_string = "\n".join(display_nodes)

    scale_attributes = results["attributes"]
    custom_scale_attributes = scale_attributes["custom_attributes"]
    del scale_attributes["custom_attributes"]
    display_attributes = []
    for att_name, att_dict in scale_attributes.items():
        items = [(k, v) for k, v in att_dict.items()]
        if len(items) == 0:
            continue
        items.sort(key=lambda x: x[1])
        item_names = "\t".join([i[0] for i in items])
        item_vals = "\t".join([f"{' '*(len(i[0])-6)}{i[1]:2.3f}" for i in items])
        display_attributes.append(
            f"{C.BOLD_BLUE}{att_name}{C.RESET}:\n {item_names}\n {item_vals}"
        )
    for att_dict in custom_scale_attributes:
        items = [(k, v) for k, v in att_dict["vals"].items()]
        items.sort(key=lambda x: x[1])
        item_names = "\t".join([i[0] for i in items])
        item_vals = "\t".join([f"{' '*(len(i[0])-6)}{i[1]:2.3f}" for i in items])
        display_attributes.append(
            f"{C.BOLD_BLUE}{att_dict['name']}{C.RESET}: {att_dict['description']}\n {item_names}\n {item_vals}"
        )
    scale_string = "\n".join(display_attributes)

    worker_name = Worker.get(db, data["worker_id"]).worker_name
    contents = data["data"]
    duration = contents["times"]["task_end"] - contents["times"]["task_start"]
    metadata_string = (
        f"Worker: {worker_name}\nUnit: {data['unit_id']}\n"
        f"Duration: {int(duration)}\nStatus: {data['status']}\n"
    )

    return (
        f"-------------------\n{metadata_string}\n{attributes_string}\n{scale_string}"
    )


def main():
    db = LocalMephistoDB()
    run_examine_or_review(db, format_data_for_printing)


if __name__ == "__main__":
    main()
