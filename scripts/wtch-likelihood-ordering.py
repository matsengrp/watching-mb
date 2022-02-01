#!/usr/bin/env python
from asyncio.subprocess import DEVNULL
import pickle
import os
from collections import namedtuple
import tempfile
import subprocess
import numpy as np
import click
import warnings

TreeData = namedtuple("TreeData", "pp_dict tree_set")


def tree_data_of_path(tree_pickle_path):
    pp_dict, tree_ci_list = pickle.load(open(tree_pickle_path, "rb"))
    return TreeData(pp_dict, set(tree_ci_list))


def optimize_branch_lengths_and_sort(tree_set, sequence_file_path):
    """
    Returns the list of trees in tree_set, with optimal branch length, ordered by
    likelihood. The first tree has the highest likelihood.
            Parameters:
                    tree_set (set): A set of trees represented as strings of their
                        Newick tree format (without branch lengths).
                    sequence_file_path (string): The file containing the sequencing
                        data for the tree tips.
            Returns:
                    optimized_trees (list): The list of trees in tree_set. Each tree
                    is represented as a string of their Newick tree format (with
                    optimal branch lengths). This list is ordered according to the
                    trees' log-likelihood from iqtree, with maximum likelihood first.
    """
    topology_file_name = "topology.nwk"
    optimized_file_name = "optimized-trees.nwk"
    likelihood_file_name = "tree-likelihoods.temp"
    with tempfile.TemporaryDirectory() as tmpdir:
        topology_path = os.path.join(tmpdir, topology_file_name)
        optimized_path = os.path.join(tmpdir, optimized_file_name)
        likelihood_path = os.path.join(tmpdir, likelihood_file_name)

        for tree in tree_set:
            # Write the tree to a temporary file.
            with open(topology_path, "w") as fp:
                fp.write(tree + "\n")
            # Run iqtree on the tree.
            subprocess.check_call(
                f"iqtree --redo --quiet -s {sequence_file_path} -te {topology_path} "
                + "-m jc69",
                shell=True,
                stderr=DEVNULL,
            )
            # !!! The command line above may throw a runtime warning:
            #       OMP: Info #271: omp_set_nested routine deprecated, please use
            #       omp_set_max_active_levels instead.
            # As best I (CJS) can tell, this is an issue with the installed version of
            # openMP. Since it is only a warning, some people say just ignore it. It
            # looks like iqtree is writing the message to standard error, rather than
            # bubbling up this warning. To suppress the message, we temporarily
            # redirect stderr. The issue is we get this message once per tree and
            # may have a couple thousands trees.

            # Add the tree with optimized branch lengths somewhere temporary, same for
            # the likelihoods. Grabbing the likelihood requires some magic to find it
            # in full report.
            subprocess.check_call(
                f"cat {sequence_file_path}.treefile >> {optimized_path}", shell=True
            )
            subprocess.check_call(
                f'grep "Log-likelihood of the tree: " {sequence_file_path}.iqtree | '
                + "sed -e 's/^Log\\-likelihood of the tree: \\(.*\\) (.*$/\\1/;'"
                + f">> {likelihood_path}",
                shell=True,
            )

        # Load all the tree info into variables and sort on likelihood.
        with open(optimized_path, "r") as the_file:
            optimized_trees = the_file.read().splitlines()
        tree_likelihoods = np.loadtxt(likelihood_path, delimiter=";", dtype=float)
        indices_for_sort = np.flip(np.argsort(tree_likelihoods))
        optimized_trees = [optimized_trees[j] for j in indices_for_sort]

        # Clean up local files.
        for extension in ["ckp.gz", "iqtree", "log", "treefile"]:
            subprocess.check_call(f"rm {sequence_file_path}.{extension}", shell=True)

        return optimized_trees


@click.command()
@click.option("--file-type", type=click.Choice(["nwk", "pkl"]), default="nwk")
@click.argument("tree_path")
@click.argument("fasta_path")
@click.argument("output_path")
def wrapper_for_tree_ordering(file_type, tree_path, fasta_path, output_path):
    if file_type == "nwk":
        with open(tree_path, "r") as the_file:
            tree_data = the_file.read().splitlines()
    elif file_type == "pkl":
        # This is old functionality and probably shouldn't be called.
        tree_data = tree_data_of_path(tree_path).tree_set

    optimized_trees = optimize_branch_lengths_and_sort(tree_data, fasta_path)

    with open(output_path, "w") as the_output_file:
        for tree in optimized_trees:
            the_output_file.write(f"{tree}\n")


if __name__ == "__main__":
    wrapper_for_tree_ordering()
