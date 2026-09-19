import tempfile
import unittest
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix

from natural_future_entropy import (
    clean_markdown,
    collect_samples,
    deterministic_folds,
    permutation_smoothness,
)


class MarkdownProtocolTests(unittest.TestCase):
    def test_clean_markdown_removes_frontmatter_and_code(self):
        raw = """---
type: Technical Paper
title: Example
---
# Heading
A natural sentence with a [link](https://example.com) in it.
```python
secret = 123
```
Another sentence with `inline_code` removed.
"""
        cleaned = clean_markdown(raw)
        self.assertNotIn("Technical Paper", cleaned)
        self.assertNotIn("secret", cleaned)
        self.assertNotIn("inline_code", cleaned)
        self.assertIn("A natural sentence with a link in it.", cleaned)
        self.assertIn("Another sentence", cleaned)

    def test_collect_samples_uses_at_most_one_excerpt_per_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            text = " ".join(f"word{i}" for i in range(220))
            for index in range(4):
                (root / f"paper{index}.md").write_text(text, encoding="utf-8")
            samples = collect_samples(root, max_files=10)
            self.assertEqual(len(samples), 4)
            self.assertEqual(len({sample.path for sample in samples}), 4)
            self.assertTrue(all(len(sample.excerpt.split()) == 140 for sample in samples))


class SpectralStatisticTests(unittest.TestCase):
    def test_smooth_path_signal_beats_permutations(self):
        n = 40
        weights = np.zeros((n, n), dtype=float)
        for index in range(n - 1):
            weights[index, index + 1] = 1.0
            weights[index + 1, index] = 1.0
        degree = weights.sum(axis=1)
        inv = 1.0 / np.sqrt(degree)
        laplacian = np.eye(n) - inv[:, None] * weights * inv[None, :]
        values = np.linspace(-1.0, 1.0, n)
        result = permutation_smoothness(laplacian, values, seed=7, repeats=199)
        self.assertLessEqual(result["energy_lower_tail_p"], 0.05)
        self.assertLessEqual(result["low_power_upper_tail_p"], 0.05)

    def test_fold_assignment_is_deterministic_and_complete(self):
        paths = [f"paper-{index}.md" for index in range(100)]
        first = deterministic_folds(paths)
        second = deterministic_folds(paths)
        np.testing.assert_array_equal(first, second)
        self.assertEqual(set(first.tolist()), {0, 1, 2, 3, 4})


if __name__ == "__main__":
    unittest.main()
