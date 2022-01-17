#!/usr/bin/env python

import bito
import json
import tempfile
import pickle
import click
import os


def write_stats(pickle_path, out_stats_path):
    pp_dict, tree_ci_list = pickle.load(open(pickle_path, "rb"))

    with tempfile.TemporaryDirectory() as tmpdir:
        ci_path = os.path.join(tmpdir, "ci_trees.nwk")
        with open(ci_path, "w") as fp:
            for tree in tree_ci_list:
                fp.write(tree + "\n")

        inst = bito.gp_instance(os.path.join(tmpdir, "mmap.dat"))
        inst.read_newick_file(ci_path)
        inst.make_dag()
        inst.print_status()
        stats = inst.dag_summary_statistics()
        stats["CI size"] = len(tree_ci_list)

        with open(out_stats_path, "w") as fp:
            fp.write(json.dumps(stats, indent=4))
            fp.write("\n")


@click.command()
@click.argument("pickle_path")
@click.argument("out_stats_path")
def cli(pickle_path, out_stats_path):
    """
    Read a pickle file from a golden run, and spit out statistics describing its DAG.
    """
    write_stats(pickle_path, out_stats_path)


if __name__ == "__main__":
    cli()
