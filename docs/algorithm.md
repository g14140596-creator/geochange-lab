# Algorithm notes

## 1. Registration

The same location may shift by a few pixels between captures. GeoChange Lab searches a
bounded grid of integer translations and minimizes normalized mean absolute grayscale
error over the valid overlap. A small displacement regularizer prevents a large shift
from winning for a negligible error reduction.

## 2. Explainable change score

For every valid pixel:

`score = 0.76 × mean absolute RGB difference + 0.24 × gradient-magnitude difference`

A 3×3 box blur reduces isolated sensor noise. The two terms are deliberately simple:
color captures surface appearance changes, while gradients capture new or removed
structure.

## 3. Adaptive decision threshold

The threshold is based on the median and median absolute deviation (MAD) of the score
map. Unlike a fixed cutoff, this adapts to quiet and noisy image pairs while remaining
robust to a small number of large changes.

## 4. Region explanations

Eight-connected components convert changed pixels into reviewable objects. Tiny
components are filtered, then each remaining region receives:

- area and bounding box;
- centroid;
- mean and maximum score;
- low, medium, or high impact severity.

## Known limitations

This prototype is a screening system. Clouds, seasons, shadows, sensor differences,
large rotations, and real geometric distortion can create false positives. A serious
deployment should add orthorectification, cloud masks, radiometric normalization, and
validation against labeled data.

