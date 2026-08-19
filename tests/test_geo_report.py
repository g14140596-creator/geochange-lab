import unittest

from geochangelab.geo import to_geojson
from geochangelab.models import Alignment, AnalysisResult, ChangeRegion
from geochangelab.report import markdown_report


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.result = AnalysisResult(
            width=100,
            height=50,
            threshold=0.12,
            changed_pixels=200,
            changed_ratio=0.04,
            alignment=Alignment(2, -1, 0.1, 0.04),
            regions=(ChangeRegion(1, 200, (20, 10, 40, 30), (30, 20), 0.4, 0.8, "medium"),),
        )

    def test_geojson_projects_to_bounds(self):
        data = to_geojson(self.result, (100.0, 20.0, 110.0, 30.0))
        ring = data["features"][0]["geometry"]["coordinates"][0]
        self.assertEqual(ring[0], [102.0, 28.0])
        self.assertEqual(data["features"][0]["properties"]["coordinate_space"], "WGS84")

    def test_report_contains_evidence_and_limitations(self):
        report = markdown_report(self.result)
        self.assertIn("1** material change region", report)
        self.assertIn("4.00%", report)
        self.assertIn("false positives", report)


if __name__ == "__main__":
    unittest.main()

