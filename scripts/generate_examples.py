#!/usr/bin/env python

"""
generate_example.py

Usage:
  generate_example.py SPEC_FILE OUT_DIR
"""
import json
import os
import os.path
from docopt import docopt
from jsonpath_rw import parse


def generate_resource_example(schema_dict, path=None):
    """
    Generates resource examples from an OAS schema

    Incomplete, especially around multiple arity/polymorphic parts such as anyOf.
    In future this should be replaced by an example generator that uses FHIR tooling.
    """
    example = {}

    if path is None:
        path = []

    for property_name, property_value in schema_dict.items():
        if property_value["type"] == "array":
            if "oneOf" in property_value["items"]:
                example[property_name] = [
                    generate_resource_example(t["properties"], path + [property_name])
                    for t in property_value["items"]["oneOf"]
                ]
            elif "anyOf" in property_value["items"]:
                example[property_name] = [
                    generate_resource_example(t["properties"], path + [property_name])
                    for t in property_value["items"]["anyOf"]
                ]
            elif property_value["items"]["type"] == "object":
                example[property_name] = [
                    generate_resource_example(
                        property_value["items"]["properties"], path + [property_name]
                    )
                ]
            else:
                if {"example", "default"} & set(property_value.get("items", {}).keys()):
                    items = property_value["items"]
                    example[property_name] = [
                        items.get("example", items.get("default"))
                    ]
                elif ("example" not in property_value) and (
                    "default" not in property_value
                ):
                    property_path = ".".join(path)
                    raise RuntimeError(
                        f"{property_path}.{property_name} has no example or default!"
                    )
                else:
                    example[property_name] = property_value.get(
                        "example", property_value.get("default")
                    )
        elif property_value["type"] == "object":
            example[property_name] = generate_resource_example(
                property_value["properties"], path + [property_name]
            )
        else:
            if ("example" not in property_value) and ("default" not in property_value):
                property_path = ".".join(path)
                raise RuntimeError(
                    f"{property_path}.{property_name} has no example or default!"
                )
            example[property_name] = property_value.get(
                "example", property_value.get("default")
            )

    return example


def main(arguments):
    """Program entry point"""
    arguments = docopt(__doc__, version="0")

    # Load spec from file
    with open(arguments["SPEC_FILE"], "r") as spec_file:
        spec = json.loads(spec_file.read())

    # Create default dir structure
    for i in ["resources", "responses"]:
        os.makedirs(os.path.join(arguments["OUT_DIR"], i), exist_ok=True)

    # Generate resources
    for component_name, component_spec in spec["components"]["schemas"].items():
        with open(
            os.path.join(arguments["OUT_DIR"], "resources", component_name + ".json"),
            "w",
        ) as out_file:
            out_file.write(
                json.dumps(
                    generate_resource_example(
                        component_spec["properties"], [component_name]
                    )
                )
            )

    # Pull out responses
    match_expr = parse(
        "paths.*.*.(response|(responses.*)).content.*.(example|(examples.*.value))"
    )

    for match in match_expr.find(spec):
        if "patch" in str(match.full_path):
            # PATCHes are not FHIR resources, so we should not be validating them
            continue

        with open(
            os.path.join(
                arguments["OUT_DIR"],
                "responses",
                str(match.full_path).replace("/", "_") + ".json",
            ),
            "w",
        ) as out_file:
            out_file.write(json.dumps(match.value))


if __name__ == "__main__":
    main(arguments=docopt(__doc__, version="0"))
