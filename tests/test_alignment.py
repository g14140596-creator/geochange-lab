import unittest

import numpy as np

from geochangelab.alignment import align_image, estimate_translation


class AlignmentTests(unittest.TestCase):
    def test_recovers_known_translation(self):
        reference = np.zeros((64, 64, 3), dtype=np.uint8)
        reference[18:40, 20:44] = (70, 180, 95)
        moving = np.zeros_like(reference)
        moving[21:43, 25:49] = (70, 180, 95)
        dx, dy, before_error, after_error = estimate_translation(reference, moving, max_shift=8, sample_step=1)
        self.assertEqual((dx, dy), (5, 3))
        self.assertLess(after_error, before_error)
        aligned, valid = align_image(moving, dx, dy)
        self.assertTrue(np.array_equal(aligned[18:40, 20:44], reference[18:40, 20:44]))
        self.assertTrue(valid[20, 20])


if __name__ == "__main__":
    unittest.main()

