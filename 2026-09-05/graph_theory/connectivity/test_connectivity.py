import unittest

from connectivity import (
    DisjointSetUnion,
    articulation_points_and_bridges,
    biconnected_components,
    connected_components,
    kosaraju_scc,
    tarjan_scc,
)


def normalized(components):
    return {frozenset(component) for component in components}


class ConnectivityTests(unittest.TestCase):
    def test_connected_components_includes_isolated_and_implicit_vertices(self):
        graph = {"a": ["b"], "b": ["a"], "c": [], "d": ["e"], "e": ["d"]}
        self.assertEqual(
            normalized(connected_components(graph)),
            {frozenset(("a", "b")), frozenset(("c",)), frozenset(("d", "e"))},
        )

    def test_scc_algorithms_agree(self):
        graph = {
            0: [1],
            1: [2, 3],
            2: [0],
            3: [4],
            4: [3],
            5: [],
        }
        expected = {frozenset((0, 1, 2)), frozenset((3, 4)), frozenset((5,))}
        self.assertEqual(normalized(kosaraju_scc(graph)), expected)
        self.assertEqual(normalized(tarjan_scc(graph)), expected)

    def test_cut_vertices_bridges_and_blocks(self):
        graph = {
            0: [1, 2],
            1: [0, 2, 3],
            2: [0, 1],
            3: [1, 4],
            4: [3],
            5: [],
        }
        cuts, bridges = articulation_points_and_bridges(graph)
        self.assertEqual(cuts, {1, 3})
        self.assertEqual(bridges, {frozenset((1, 3)), frozenset((3, 4))})
        self.assertEqual(
            normalized(biconnected_components(graph)),
            {frozenset((0, 1, 2)), frozenset((1, 3)), frozenset((3, 4)), frozenset((5,))},
        )

    def test_dsu(self):
        dsu = DisjointSetUnion("abcd")
        self.assertEqual(dsu.component_count(), 4)
        self.assertTrue(dsu.union("a", "b"))
        self.assertTrue(dsu.union("b", "c"))
        self.assertFalse(dsu.union("a", "c"))
        self.assertTrue(dsu.connected("a", "c"))
        self.assertFalse(dsu.connected("a", "d"))
        self.assertEqual(dsu.component_count(), 2)


if __name__ == "__main__":
    unittest.main()
