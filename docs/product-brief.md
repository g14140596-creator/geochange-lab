# Product brief

## User problem

Students, local planners, researchers, and community groups often have before/after
imagery but lack a transparent way to identify where to look first. Existing research
models can be difficult to install, expensive to run, or hard to explain.

## Product promise

GeoChange Lab turns a paired image inspection into a reproducible review package:
visual overlay, ranked regions, metrics, GeoJSON, and a plain-language report.

## MVP success criteria

1. Detect a synthetic material change while ignoring an identical image pair.
2. Recover small x/y translations before comparison.
3. Export the same region evidence in visual, JSON, GeoJSON, and Markdown formats.
4. Run locally with no API key and a small dependency footprint.

## Next validation steps

- Build a 30-pair mini benchmark covering construction, water, vegetation, and noise.
- Measure region precision/recall and registration error.
- Interview three remote-sensing students and two potential nontechnical users.
- Add Sentinel-2 band support and cloud masking only after validating the workflow.

