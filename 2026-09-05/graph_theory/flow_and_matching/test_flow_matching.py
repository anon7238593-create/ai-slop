import unittest
from flow_matching import bipartite_matching, max_flow, min_cut


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.network = {
            "s": {"a": 3, "b": 2}, "a": {"b": 1, "c": 2},
            "b": {"c": 2, "d": 3}, "c": {"t": 2}, "d": {"t": 3}, "t": {},
        }

    def test_edmonds_karp_and_ford_fulkerson_agree(self):
        self.assertEqual(max_flow(self.network, "s", "t", "bfs")[0], 5)
        self.assertEqual(max_flow(self.network, "s", "t", "dfs")[0], 5)
        self.assertEqual(self.network["s"]["a"], 3)  # input is immutable

    def test_min_cut_certificate(self):
        value, source_side, sink_side, flow = min_cut(self.network, "s", "t")
        self.assertEqual(value, 5)
        self.assertIn("s", source_side)
        self.assertIn("t", sink_side)
        crossing = sum(self.network[u].get(v, 0) for u in source_side for v in sink_side)
        self.assertEqual(crossing, value)
        self.assertEqual(sum(flow["s"].values()), value)

    def test_matching(self):
        matching = bipartite_matching("ABC", {1, 2, 3}, [("A", 1), ("A", 2), ("B", 2), ("C", 2), ("C", 3)])
        self.assertEqual(len(matching), 3)
        self.assertEqual(set(matching), set("ABC"))
        self.assertEqual(len(set(matching.values())), 3)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            max_flow({"s": {"t": -1}, "t": {}}, "s", "t")
        with self.assertRaises(ValueError):
            bipartite_matching(["A"], [1], [("B", 1)])


if __name__ == "__main__":
    unittest.main()
