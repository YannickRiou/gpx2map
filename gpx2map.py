#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gpx2map — turn a GPX track into a themed map picture (PNG): title, track over IGN contour
lines, lakes, elevation profile and statistics, in one of several themes: engraved wood,
sepia paper, ink wash, IGN-style topo map, dark posters (noir, midnight, blueprint, neon...)
and a realistic one that puts the IGN orthophoto under the contours.

The pipeline (engine.py, the gpx2engraving engine) and the themes (render.py) come from the
gpx2core repository, included here as the git submodule core/ (clone with --recursive).
Same options as gpx2engraving for the content and the layout, plus --theme, --dpi and
colour overrides.

    python gpx2map.py hike.gpx --title "Pic de Cagire"                 -> hike_wood.png
    python gpx2map.py hike.gpx -t "Pic de Cagire" --theme satellite    -> hike_satellite.png
    python gpx2map.py hike.gpx -t "Pic de Cagire" --theme all --dpi 150
    python gpx2map.py hike.gpx --theme noir --track-color #DBE64C --bg-color #113B54
    python gpx2map.py --list-themes
"""

import os
import sys

CORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "core")
if not os.path.isfile(os.path.join(CORE, "engine.py")):
    sys.exit("core/engine.py is missing: run `git submodule update --init` "
             "(or clone with --recursive) to fetch gpx2core.")
sys.path.insert(0, CORE)
import engine   # noqa: E402
import render   # noqa: E402


def main():
    if "--list-themes" in sys.argv:
        render.print_themes()
        return
    ap = engine.build_parser(add_output=False, description="GPX -> themed map picture (PNG).")
    ap.add_argument("--out", "-o", help="output PNG (single theme; default: <Title>_<theme>.png next to the first GPX)")
    ap.add_argument("--out-dir", help="folder for the default file names")
    ap.add_argument("--dpi", type=int, default=300, help="output resolution (the plate size in mm is kept)")
    render.add_theme_options(ap)
    args = ap.parse_args()
    themes = render.theme_list(args.theme)
    if args.out and len(themes) > 1:
        ap.error("--out needs a single theme")
    overrides = render.overrides_from_args(args)

    plate = engine.build(args)
    out_dir = args.out_dir or os.path.dirname(os.path.abspath(plate.files[0]["path"]))
    os.makedirs(out_dir, exist_ok=True)
    for th in themes:
        out = args.out or os.path.join(out_dir, f"{plate.slug}_{th}.png")
        render.save_png(plate, th, out, dpi=args.dpi, cache_dir=args.cache_dir, overrides=overrides,
                        labels=not args.no_labels, label_size_mm=args.map_label_size)
        engine.log(f"PNG written ({th}): {out}")


if __name__ == "__main__":
    main()
