#!/usr/bin/env python
import numpy as np
import igraph
import click
import multiprocessing
from sortedcontainers import SortedList
from functools import partial


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

    def _make_generator(reader):
        while True:
            b = reader(2**16)
            if not b:
                break
            yield b

    with open(file_path, "rb") as the_file:
        count = sum(
            buffer.count(b"\n") for buffer in _make_generator(the_file.raw.read)
        )
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


def load_trees(file_path, with_likelihoods=False):
    """Loads in the tree data from file_path. The expected file format of file_path
    is one tree per line, each line consists of i) a comma separated list of integers
    of the subsplit dag node indices comprising the tree; ii) another comma followed by
    nothing when with_likelihoods is False and the log-likelihood of the tree
    when with_likelilihooods is True; and iii) the newline character \\n (even the final
    line should have the newline character). The subsplit dag is not seen by any of
    this code, so it is only assumed that the trees are all from a common sdag and the
    node indices are correct.

    :return: A pair (T,L), where T is a python list of integers encoding each tree's
        subsplit dag node representation and L is a numpy.array of each tree's
        log-likelihood. When with_likelihoods is True, both T and L are sorted in
        descending order according to log-likelihood. When with_likelihoods is False,
        L is a vector of zeros.
    :rtype: tuple
    """
    n_rows = fast_line_count(file_path)
    # We use a python list of ints for tree_bit_list because Python does not have a
    # maximum int size, but a numpy array of ints does.
    tree_bit_list = []
    tree_log_likelihood_array = np.zeros(n_rows, dtype=float)
    if not with_likelihoods:
        # In bito, reps_and_likelihoods uses SIZE_MAX for unknown subsplits.
        invalid_index = 2**64 - 1
        with open(file_path, "rt") as the_file:
            for line in the_file:
                sdag_info = line[:-2].split(",")
                sdag_info = [int(c) for c in sdag_info]
                if invalid_index not in sdag_info:
                    tree_bit_list.append(encode_sdag_nodes_as_int(sdag_info))
    else:
        with open(file_path, "rt") as the_file:
            for j, line in enumerate(the_file):
                sdag_info = line[:-1].split(",")
                tree_bit_list.append(encode_sdag_nodes_as_int(map(int, sdag_info[:-1])))
                tree_log_likelihood_array[j] = float(sdag_info[-1])
        new_indices = tree_log_likelihood_array.argsort()[::-1]
        tree_bit_list = [tree_bit_list[j] for j in new_indices]
        tree_log_likelihood_array = tree_log_likelihood_array[new_indices]
    return (tree_bit_list, tree_log_likelihood_array)


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
def find_likely_neighbors(
    sdag_rep_path,
    output_path,
    extra_trees_path=None,
    max_tree_count=0,
    max_tree_ratio=0.0,
):
    """
    Determine a list of of trees that are nearest neighbor interchanges of each other
    with high likelihood. The data for the trees are in sdag_rep_path and this file
    must follow the format explained in the documentation for
    load_trees(file_path, True). The optional parameter extra_trees_path specifies a
    file of trees, following the format specified for load_trees(file_path, False),
    with which to start the walk along with the highest likelihood tree.
    The optional parameters max_tree_count and max_tree_ratio indicate to use only the
    the first max_tree_count (max_tree_ratio, respectively) after sorting the trees
    by log-likelihood. When max_tree_count and max_tree_ratio are both given, the more
    restrictive condition is used.
    """
    tree_bits_list, log_likelihoods = load_trees(sdag_rep_path, True)
    vertex_count = len(tree_bits_list)

    if max_tree_ratio > 0:
        vertex_count = min(vertex_count, int(np.floor(max_tree_ratio * vertex_count)))
    if max_tree_count > 0:
        vertex_count = min(vertex_count, max_tree_count)
    the_graph = igraph.Graph(vertex_count)
    the_graph.vs["encoded_sdag_representation"] = tree_bits_list[:vertex_count]
    the_graph.vs["log_likelihood"] = log_likelihoods[:vertex_count]
    tree_bits_list = None
    log_likelihoods = None

    # For the cluster, 16 processes works well.
    with multiprocessing.Pool(processes=16) as pool:
        partial_find_nni_trees = partial(
            find_nni_trees, tree_bits_list=the_graph.vs["encoded_sdag_representation"]
        )
        edges = pool.map(partial_find_nni_trees, range(vertex_count - 1))
    for edge_list in edges:
        the_graph.add_edges(edge_list)
    # At this point, the graph is fully constructed.

    extras = [] if extra_trees_path is None else load_trees(extra_trees_path, False)[0]
    extra_nodes = the_graph.vs.select(encoded_sdag_representation_in=extras)
    good_vertex_indices = max_weight_neighbor_traversal(
        the_graph, "log_likelihood", extra_nodes
    )

    with open(output_path, "wt") as out_file:
        for vertex in the_graph.vs[good_vertex_indices]:
            sdag_rep = decode_int_as_sdag_nodes(vertex["encoded_sdag_representation"])
            out_file.write(
                ",".join(map(str, sdag_rep)) + f",{vertex['log_likelihood']}" + "\n"
            )

    return None


if __name__ == "__main__":
    find_likely_neighbors()
