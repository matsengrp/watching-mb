#!/usr/bin/env python
import numpy as np
import igraph
import click
import multiprocessing
from sortedcontainers import SortedList
from functools import partial
import os
import sys

# This funny business with paths is needed because this file is intended to be called
# from the command line by a sym link in $CONDA_PREFIX/bin, but naively python does not
# know to check that directory for parsimony.py.
sys.path.append(os.path.dirname(__file__))
from parsimony import load_fasta, build_tree, sankoff_upward


# A note on igraph and indexing:
# The module igraph keeps track of the vertices using contiguous indexing. So
# when vertices are deleted or moved around, the indices may change. But vertices are
# allowed attibutes and attributes are exposed as dictionaries. For an attribute
# specifically named "name", igraph does indexing based on this attribute in amortized
# constant time, so working with vertices based on the attribute "name" is a safe and
# fast way to go when there may be issues with indices. But there are two issues.
# 1) There are different behaviors if attribute "name" is string or an int. When a
# vertex has the "name" attribute with value "10", the_graph.vs.find(name="10") and
# the_graph.vs.find("10") yield the vertex with name "10", and the_graph.vs[10] yields
# the vertex at index 10. When a vertex has the "name" attribute with value 10,
# the_graph.vs.find(name=10) yields the vertex with name 10, whereas
# the_graph.vs.find(10) and the_graph.vs[10] yield the vertex at index 10.
# 2) The values of the attribute "name" need not be unique.


def fast_line_count(file_path):
    """Returns the number of lines in file_path. This method is as fast as invoking
    wc -l.
    """

    def _make_gen(reader):
        while True:
            b = reader(2**16)
            if not b:
                break
            yield b

    with open(file_path, "rb") as the_file:
        count = sum(buffer.count(b"\n") for buffer in _make_gen(the_file.raw.read))
    return count


def encode_sdag_nodes_as_int(sdag_node_list):
    """Given a list of integers, which represent specific nodes of some subsplit dag,
    construct an integer that represents this list. In the base 2 representation of the
    returned integer, the digit at entry j (reading from right to left and with the far
    right digit being at entry 0) is 1 exactly when j is in sdag_node_list.

    E.g.: [5,2,0,1] -> 100111 -> 2^5+2^2+2^1+2^0 = 39
    """
    return sum(2**n for n in sdag_node_list)


def decode_int_as_sdag_nodes(the_int):
    """This is the inverse function of encode_sdag_nodes_as_int, up to list ordering."""
    bit_string = bin(the_int)[::-1]
    return [j for j in range(the_int.bit_length()) if bit_string[j] == "1"]


def build_and_score(nwk, fasta_map):
    """Returns the parsimony score for the given newick string and custom fasta_map."""
    return sankoff_upward(build_tree(nwk, fasta_map), gap_as_char=False)


def parsimony_scores(nwk_list, fasta_map):
    """
    Returns the parsimony scores for the given list of newick strings and custom
    fasta_map.
    """
    informative_sites = [
        idx for idx, chars in enumerate(zip(*fasta_map.values())) if len(set(chars)) > 1
    ]
    newfasta = {
        key: "".join(oldseq[idx] for idx in informative_sites)
        for key, oldseq in fasta_map.items()
    }
    with multiprocessing.Pool(processes=16) as pool:
        partial_build_and_score = partial(build_and_score, fasta_map=newfasta)
        scores = pool.map(partial_build_and_score, nwk_list)
    return scores


def compute_parsimony_scores_from_files(nwk_path, fasta_path):
    """
    Returns the parsomony scores for the newick strings in the file nwk_path using the
    fasta file located at fasta_path.
    """
    nwk_list = read_nwk(nwk_path)
    fasta_map = load_fasta(fasta_path)
    return parsimony_scores(nwk_list, fasta_map)


def read_nwk(nwk_path):
    """Returns the list of newick strings in the file nwk_path."""
    tree_nwk_list = []
    with open(nwk_path) as the_file:
        for line in the_file:
            tree_nwk_list.append(line.strip())
    return tree_nwk_list


def read_sdag_rep_trees(file_path, with_likelihoods=False):
    """
    Loads the tree data from file_path. The expected file format of file_path is one
    tree per line, each line consists of i) a comma separated list of integers of the
    subsplit dag node indices comprising the tree; ii) another comma; iii) nothing when
    with_likelihoods=False and the log-likelihood of the tree when
    with_likelilihooods=True; and iv) the newline character \\n (even the final line
    should have the newline character).

    Since the subsplit DAG is not seen by any of this code, it is assumed that the trees
    are all from a common sDAG and the node indices are correct. Trees that are not in
    this commond sDAG are identified by an invalid sDAG node index and are omitted from
    the returned values.

    :return: A pair (T,L), where T is a python list of integers encoding each tree's
        subsplit DAG node representation (a single integer is used for a single tree),
        and L is a numpy.array of each tree's log-likelihood. When
        with_likelihoods=False, L is a vector of zeros. When with_likelihoods=True, both
        T and L are sorted in descending order according to log-likelihood.
    :rtype: tuple
    """
    n_rows = fast_line_count(file_path)
    # In bito, reps_and_likelihoods uses SIZE_MAX for unknown subsplits.
    invalid_index = 2**64 - 1
    tree_bit_list = []
    tree_likelihood_array = np.zeros(n_rows, dtype=float)
    with open(file_path, "rt") as the_file:
        for j, line in enumerate(the_file):
            tree_info = line.strip().split(",")
            sdag_rep = [int(c) for c in tree_info[:-1]]
            if invalid_index not in sdag_rep:
                tree_bit_list.append(encode_sdag_nodes_as_int(sdag_rep))
                if with_likelihoods:
                    tree_likelihood_array[j] = float(tree_info[-1])
    return tree_bit_list, tree_likelihood_array


def process_trees(
    file_path,
    with_likelihoods=False,
    use_parsimony=False,
    nwk_path=None,
    fasta_path=None,
):
    """
    Loads the tree data from file_path (according to the method read_sdag_rep_trees).
    If either with_likelihoods or use_parsimony is true, then both an integer list
    encoding the trees and a numpy array of the statistic are returned and both are
    sorted according to the statistic. When both with_likelihoods and use_parsimony are
    false, only the list of integers encoding the trees is returned. Both nwk_path and
    fasta_path are required when use_parsimony=True.

    When using parsimony scores, the negative of the parsimony score is returned. This
    is done so that the ordering is always descending (high likelihood is good, whereas
    low parsimony is good).
    """
    if with_likelihoods and use_parsimony:
        raise ValueError("process_trees cannot use both likelihood and parsimony")
    if use_parsimony and (nwk_path is None or fasta_path is None):
        raise ValueError("process_trees requires nwk_path and fasta_path for parsimony")

    tree_bit_list, tree_scores = read_sdag_rep_trees(file_path, with_likelihoods)
    if use_parsimony:
        tree_scores = compute_parsimony_scores_from_files(nwk_path, fasta_path)
        tree_scores = np.array([-p for p in tree_scores])
    if with_likelihoods or use_parsimony:
        new_indices = tree_scores.argsort()[::-1]
        tree_bit_list = [tree_bit_list[j] for j in new_indices]
        tree_scores = tree_scores[new_indices]
        return tree_bit_list, tree_scores
    else:
        return tree_bit_list


def are_nni_related(this_int, that_int):
    """Determine if two integers represent trees that are a single NNI operation away
    from each other (in the common subsplit dag).
    """
    return bin(this_int ^ that_int).count("1") <= 10


def find_nni_trees(j, tree_bits_list):
    """Returns a list of pairs (j,k), where the integers tree_bits_list[j]
    and tree_bits_list[k] represent trees that are single NNI operation away
    from each other. This method is designed for multiprocessing on j.
    """
    return [
        (j, k)
        for k in range(j + 1, len(tree_bits_list))
        if are_nni_related(tree_bits_list[j], tree_bits_list[k])
    ]


def max_weight_neighbor_traversal(graph, weight_attribute, start_trees=[]):
    """Calculate a list of vertex indices from graph with large weight_attribute
    values. More precisely, the list begins with a vertex of maximal weight_attribute
    value, along with the vertices in start_trees, and each later element of the list
    has maximal weight_attribute value among the neighors of all earlier elements.

    :type graph: igraph.Graph
    """
    if graph.vcount() == 0:
        return []
    current_vertex = graph.vs[np.argmax(graph.vs[weight_attribute])]
    visited_vertices = [] if current_vertex in start_trees else [current_vertex]
    visited_vertices.extend(start_trees)
    unvisited_neighbors = SortedList(key=lambda v: -v[weight_attribute])
    unvisited_neighbors.update(
        {
            n
            for c in visited_vertices
            for n in c.neighbors()
            if n not in visited_vertices
        }
    )

    while len(unvisited_neighbors) > 0:
        current_vertex = unvisited_neighbors.pop(0)
        visited_vertices.append(current_vertex)
        unvisited_neighbors.update(
            [
                neighbor
                for neighbor in current_vertex.neighbors()
                if neighbor not in visited_vertices
                and neighbor not in unvisited_neighbors
            ]
        )
    vertex_indices = [v.index for v in visited_vertices]

    return vertex_indices


@click.command()
@click.argument("sdag_rep_path")
@click.argument("output_path")
@click.option("--extra_trees_path", default=None)
@click.option("--max_tree_count", default=0)
@click.option("--max_tree_ratio", default=0.0)
@click.option("--use_parsimony", default=False, is_flag=True)
@click.option("--nwk_path", default=None)
@click.option("--fasta_path", default=None)
def find_likely_neighbors(
    sdag_rep_path,
    output_path,
    extra_trees_path=None,
    max_tree_count=0,
    max_tree_ratio=0.0,
    use_parsimony=False,
    nwk_path=None,
    fasta_path=None,
):
    """
    Determine a list of trees that are nearest neighbor interchanges of each other with
    high likelihood (or low parsimony score when use_parsimony=True). The trees and
    scores are loaded according to the method process_trees. The optional parameter
    extra_trees_path specifies a file of trees with which to start the list along with
    the best scored tree. The optional parameters max_tree_count and max_tree_ratio
    indicate to use only the first max_tree_count (max_tree_ratio, respectively) after
    sorting the trees. When max_tree_count and max_tree_ratio are both given, the more
    restrictive condition is used. The list of trees is determined by the method
    max_weight_neighbor_traversal.
    """
    weight_attr = "parsimony" if use_parsimony else "log_likelihood"

    tree_bits_list, tree_scores = process_trees(
        sdag_rep_path,
        with_likelihoods=not use_parsimony,
        use_parsimony=use_parsimony,
        nwk_path=nwk_path,
        fasta_path=fasta_path,
    )

    vertex_count = len(tree_bits_list)
    if max_tree_ratio > 0:
        vertex_count = min(vertex_count, int(np.floor(max_tree_ratio * vertex_count)))
    if max_tree_count > 0:
        vertex_count = min(vertex_count, max_tree_count)
    the_graph = igraph.Graph(vertex_count)
    the_graph.vs["encoded_sdag_representation"] = tree_bits_list[:vertex_count]
    the_graph.vs[weight_attr] = tree_scores[:vertex_count]
    tree_bits_list = None
    tree_scores = None

    # For the cluster, 16 processes works well.
    with multiprocessing.Pool(processes=16) as pool:
        partial_find_nni_trees = partial(
            find_nni_trees, tree_bits_list=the_graph.vs["encoded_sdag_representation"]
        )
        edges = pool.map(partial_find_nni_trees, range(vertex_count - 1))
    for edge_list in edges:
        the_graph.add_edges(edge_list)
    # At this point, the graph is fully constructed.

    extras = [] if extra_trees_path is None else process_trees(extra_trees_path)
    extra_nodes = the_graph.vs.select(encoded_sdag_representation_in=extras)

    good_vertex_indices = max_weight_neighbor_traversal(
        the_graph, weight_attr, extra_nodes
    )

    with open(output_path, "wt") as out_file:
        for vertex in the_graph.vs[good_vertex_indices]:
            sdag_rep = decode_int_as_sdag_nodes(vertex["encoded_sdag_representation"])
            out_file.write(
                ",".join(map(str, sdag_rep)) + f",{vertex[weight_attr]}" + "\n"
            )

    return None


if __name__ == "__main__":
    find_likely_neighbors()
