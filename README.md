# jupiter
Generate "Jupiter" plots for circular genomes

## Description

Python scripts to generate plots from [ViennaRNA](https://github.com/ViennaRNA) output.   

Written in "pidgin" python with no external dependencies (no third-party libaries).   

Generating a plot is a two-step process. Input is a ViennaRNA postscript (ps) file. The first
step converts ps to TSV, the second step converts TSV to SVG.

## jupiter_ps2tsv.py

`python3 jupiter_ps2tsv.py vienna.ps > vienna.tsv`

## jupiter_tsv2svg.py

`python3 jupiter_tsv2svg.py vienna.tsv [configfile] > vienna.svg`

## TSV file format

TSV fields are:

1. i	Base postion 0, 1 ... (L-1) where L is genome length.   
2. x	x coordinate.   
3. y	y coordinate.   
4. S	S array from ps file (Score?).   
5. j	Position of paired base, or period '.' if unpaired.   

The x,y coordinates are position of a base on a circle, they
are re-scaled to range from zero to one so the circle diameter
is one and the circle center is x=0.5, y=0.5.

## Config file format

The optional configfile is used to set rendering style. Format is tab-separated
text where the first field is the parameter name and subsequent fields (usually
just one) gives the value(s). Parameters are:

`line  `	Line width, floating point, default 1.   
`bend  `	Sets "bendiness" of the arcs, default 1.   
`hb    `	Bezier handle offset, default 1.   
`colors`	heatmap colors, default 0x0000ff    0x00ff00    0xffff00    0xff0000   

All parameters are optional and may be specified in any order.

Example config file:

`line    0.5`   
`bend    2.2`   
`colors  0x000000    0x500000    0x900000    0xff0000`   
