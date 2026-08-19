import unittest

import numpy as np

from geochangelab import AnalysisConfig, analyze_images


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.before = np.full((96, 128, 3), (80, 125, 72), dtype=np.uint8)
        self.before[12:22, :] = (95, 102, 108)

    def test_identical_images_have_no_regions(self):
        result, _, mask, _ = analyze_images(self.before, self.before.copy(), AnalysisConfig(max_shift=0))
        self.assertEqual(result.changed_pixels, 0)
        self.assertEqual(len(result.regions), 0)
        self.assertFalse(mask.any())

    def test_detects_material_rectangle(self):
        after = self.before.copy()
        after[42:70, 52:92] = (220, 220, 210)
        result, overlay, mask, _ = analyze_images(
            self.before, after, AnalysisConfig(max_shift=0, min_area=30)
        )
        self.assertGreaterEqual(len(result.regions), 1)
        largest = result.regions[0]
        self.assertGreater(largest.area_pixels, 700)
        self.assertTrue(48 <= largest.bbox[0] <= 56)
        self.assertEqual(overlay.shape, self.before.shape)
        self.assertTrue(mask[55, 70])


if __name__ == "__main__":
    unittest.main()

