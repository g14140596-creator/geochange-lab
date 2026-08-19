# Contributing

1. Create a focused branch and explain the user problem in the pull request.
2. Add or update tests for behavior changes.
3. Run `python -m unittest discover -s tests -v` and `ruff check .`.
4. Keep the core pipeline interpretable; document any learned model and its data.

Good first issues include image-size normalization, cloud-mask adapters, GeoTIFF
metadata support, and benchmark datasets with clear licenses.

