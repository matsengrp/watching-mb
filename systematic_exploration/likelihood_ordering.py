import pickle
import bito
import json
import os
from collections import namedtuple
import tempfile
import subprocess
import numpy as np
import click


TreeData = namedtuple("TreeData", "pp_dict tree_set")


def tree_data_of_path(tree_pickle_path):
    pp_dict, tree_ci_list = pickle.load(open(tree_pickle_path, "rb"))
    return TreeData(pp_dict, set(tree_ci_list))


def optimize_branch_lengths_for_tree_set(tree_set, sequence_file_path):
    '''
    Returns a list of pairs (T,L) for each tree T in the tree set, with L the log-likelihood from optimized
    branch lengths on T. This list is ordered on L, so the first tree has the highest likelihood.
            Parameters:
                    tree_set (set): A set of trees represented as strings of their Newick tree format (without branch lengths).
                    sequence_file_path (string): The file containing the sequencing data for the tree tips.
            Returns:
                    trees_and_likelihoods (list): The list of (tree, log-likelihood) pairs for each tree in tree_set. Each tree
                    is represented as a string of their Newick tree format (with optimal branch lengths). This list is
                    ordered according to the trees' log-likelihood, with maximum likelihood first.
    '''
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
            subprocess.check_call(f"iqtree --redo --quiet -s {sequence_file_path} -te {topology_path} -m jc69", shell=True)
            # !!! The line above may throw a runtime warning:
            #       OMP: Info #271: omp_set_nested routine deprecated, please use omp_set_max_active_levels instead.
            # As best I (CJS) can tell, this is an issue with which version of openMP is installed. Since it is only a warning,
            # some people say just ignore it.
     
            # Add the tree with optimized branch lengths somewhere temporary, same for the likelihoods.
            # Grabbing the likelihood requires some magic to find it in full report.
            subprocess.check_call(f"cat {sequence_file_path}.treefile >> {optimized_path}", shell=True)
            subprocess.check_call(f"grep \"Log-likelihood of the tree: \" {sequence_file_path}.iqtree | "
                + "sed -e 's/^Log\\-likelihood of the tree: \\(.*\\) (.*$/\\1/;'"
                + f">> {likelihood_path}", shell=True)

        # Load all the tree info into variables, sort on likelihood, and return.
        with open(optimized_path, "r") as the_file:
            optimized_trees = the_file.read().splitlines()
        tree_likelihoods = np.loadtxt(likelihood_path, delimiter=";", dtype=float)
        trees_and_likelihoods = list(zip(optimized_trees, tree_likelihoods))
        trees_and_likelihoods.sort(reverse=True, key=lambda x:x[1])
        
        # Clean up local files.
        for extension in ["ckp.gz", "iqtree", "log", "treefile"]:
            subprocess.check_call(f"rm {sequence_file_path}.{extension}", shell=True)

        return trees_and_likelihoods


@click.command()
@click.argument("posterior_pickle_path")
@click.argument("fasta_path")
@click.argument("output_path")
def wrapper(posterior_pickle_path, fasta_path, output_path):
    tree_data = tree_data_of_path(posterior_pickle_path)
    temp = optimize_branch_lengths_for_tree_set(tree_data.tree_set, fasta_path)
    n = len(temp)
    with open(output_path, "w") as the_output_file:
        for entry in temp[:n-1]:
            the_output_file.write(f"{entry},\n")
        entry = temp[n-1]
        the_output_file.write(f"{entry}")


if __name__=="__main__":
    wrapper()
