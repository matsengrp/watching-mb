#!/usr/bin/env python

import json
import click

@click.command()
@click.argument("json_in_path")
@click.argument("json_out_path")
@click.argument("attribute")
@click.argument("value")
def quick_edit(json_in_path, json_out_path, attribute, value):
    with open(json_in_path) as json_file:
        json_decoded = json.load(json_file)

    json_decoded[attribute] = value

    with open(json_out_path, "w") as json_file:
        json.dump(json_decoded, json_file, indent=4)
        json_file.write("\n")

if __name__=="__main__":
    quick_edit()


