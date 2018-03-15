#! /bin/bash -ex

# This is a quick-and dirty script; may not work for you

rm -fv *.pdf
python2 ~/dev/svg-objects-export/svg-objects-export.py --xpath "//svg:g[@inkscape:groupmode='layer']" \
	--extra '--export-area-page --export-id-only --export-background=#FFFFFFFF' \
	-t pdf slides/slides.svg
mutool merge -o slides.pdf slides_l*.pdf

