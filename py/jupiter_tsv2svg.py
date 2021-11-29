#!/usr/bin/python3

import sys
import math

'''
Generate SVG "Jupiter" figure from a TSV file. 
The TSV is created by jupiter_ps2tsv.py.

Usage:

python3 jupiter_tsv2svg.py vienna.tsv [configfile] > vienna.svg

The optional configfile is used to set rendering style. Format is tab-separated
text where the first field is the parameter name and subsequent fields (usually
just one) gives the value(s). Parameters are:

	line	Line width, floating point, default 1.
	bend	Sets "bendiness" of the arcs, default 1.
	hb		Bezier handle offset, default 1.
	colors	heatmap colors, default 0x0000ff    0x00ff00    0xffff00    0xff0000

All parameters are optional and may be specified in any order.

Example config file:

line    0.5
bend    2.2
colors  0x000000    0x500000    0x900000    0xff0000
'''

# STYLE = "straightlines"
STYLE = "bezier"

LINE_WIDTH = 1
BEND = 1
HANDLE_B = 1
COLORS = [ 0x0000ff, 0x00ff00, 0xffff00, 0xff0000 ]

# Dimensions are for canonical genome length, figure will be bigger
# or smaller in proportion to actual length
CIRCLE_DIAMETER = 300
CANONICAL_GENOME_LENGTH = 600
HORIZ_MARGIN = 5
VERT_MARGIN = 5
SCALE = 3
FLARE = 3
HeatMapValues =	[ 0, 0.333,	0.666, 1]

Title = None
if len(sys.argv) > 3:
	Title = sys.argv[3]

def ReadConfigFile(FileName):
	global LINE_WIDTH
	global BEND
	global HANDLE_B
	global COLORS

	for Line in open(FileName):
		Fields = Line[:-1].split("\t")
		Param = Fields[0]
		if Param == "line":
			LINE_WIDTH = float(Fields[1])
		elif Param == "bend":
			BEND = float(Fields[1])
		elif Param == "hb":
			HANDLE_B = float(Fields[1])
		elif Param == "flare":
			FLARE = float(Fields[1])
		elif Param == "colors":
			for i in range(0, 4):
				x = int(Fields[1+i], 0)
				COLORS[i] = x

if len(sys.argv) > 2:
	ConfigFileName = sys.argv[2]
	ReadConfigFile(ConfigFileName)

def HexToRGB(H):
	B = H%0x100
	h = (H - B)//0x100
	G = h%0x100
	h = h - G
	R = h//0x100

	assert R <= 255
	assert G <= 255
	assert B <= 255

	return R, G, B

Rs = []
Gs = []
Bs = []
for i in range(0, 4):
	R, G, B = HexToRGB(COLORS[i])
	Rs.append(R)
	Gs.append(G)
	Bs.append(B)

def GetSvgCircle(x, y, r, LineColor = "black", FillColor = "none"):
	return r'<circle cx="%.6g" cy="%.6g" r="%.6g" stroke-width="%.6g" stroke="%s" fill="%s" />' % \
	  (x, y, r, LINE_WIDTH, LineColor, FillColor)

def GetSvgLine(x1, y1, x2, y2, Color = "black"):
	return r'<line x1="%.6g" y1="%.6g" x2="%.6g" y2="%.6g" stroke-width="%.6g" stroke="%s" />' % \
	  (x1, y1, x2, y2, LINE_WIDTH, Color)

def RescaleToGenomeLength(GenomeLength):
	global CIRCLE_DIAMETER
	global LINE_WIDTH

	r = GenomeLength/(CANONICAL_GENOME_LENGTH*SCALE)
	CIRCLE_DIAMETER *= r
	## LINE_WIDTH *= r
	LINE_WIDTH *= 0.4

# https://medium.com/@bragg/cubic-bezier-curves-with-svg-paths-a326bb09616f
def GetBezierHandleCoords(Xi, Yi, Xj, Yj):
	Mx = (Xi + Xj)/2
	My = (Yi + Yj)/2

	CIRCLE_RADIUS = CIRCLE_DIAMETER/2
	Cx = CIRCLE_BOUNDING_BOX_LEFT + CIRCLE_RADIUS
	Cy = CIRCLE_BOUNDING_BOX_TOP + CIRCLE_RADIUS

	Diff_x = Xi - Xj
	Diff_y = Yi - Yj
	Dist_ij = math.sqrt(Diff_x**2 + Diff_y**2)

	B0 = BEND*0.002

	dx = (Cx - Mx)*B0*Dist_ij
	dy = (Cy - My)*B0*Dist_ij

	Dx = Xi + dx
	Dy = Yi + dy

	Ex = Xj + dx
	Ey = Yj + dy

	MidDEx = (Dx + Ex)/2
	MidDEy = (Dy + Ey)/2

	B1 = HANDLE_B
	B2 = 1
	B12 = B1 + B2

	Fx = (B1*Dx + B2*MidDEx)/B12
	Fy = (B1*Dy + B2*MidDEy)/B12

	Gx = (B1*Ex + B2*MidDEx)/B12
	Gy = (B1*Ey + B2*MidDEy)/B12

	if 0:
		print(GetSvgCircle(Cx, Cy, 1, "none", "blue"))
		print(GetSvgCircle(MidDEx, MidDEy, 1, "none", "skyblue"))

		print(GetSvgCircle(Xi, Yi, 1, "none", "red"))
		print(GetSvgCircle(Fx, Fy, 1, "none", "darkred"))
		print(GetSvgLine(Xi, Yi, Fx, Fy, "red"))

		print(GetSvgCircle(Xj, Yj, 1, "none", "lightgreen"))
		print(GetSvgCircle(Gx, Gy, 1, "none", "darkgreen"))
		print(GetSvgLine(Xj, Yj, Gx, Gy, "green"))

	return Fx, Fy, Gx, Gy

######################################################
# GetColor(): Generate heat map color by interpolation
######################################################
def GetColor(Value):
	assert Value >= 0 and Value <= 1
	N = len(HeatMapValues)
	assert len(Rs) == N
	assert len(Gs) == N
	assert len(Bs) == N

	for i in range(1, N):
		LoValue = HeatMapValues[i-1]
		HiValue = HeatMapValues[i]
		assert LoValue < HiValue
		if Value >= LoValue and Value <= HiValue:
			f = float(Value - LoValue)/float(HiValue - LoValue)
			assert f >= 0.0 and f <= 1.0
			R = int((Rs[i] - Rs[i-1])*f + Rs[i-1])
			G = int((Gs[i] - Gs[i-1])*f + Gs[i-1])
			B = int((Bs[i] - Bs[i-1])*f + Bs[i-1])
			assert R >= 0 and R <= 255
			assert G >= 0 and G <= 255
			assert B >= 0 and B <= 255
			Str = "#%02x%02x%02x" % (R, G, B)
			return Str
	assert False
######################################################

def fix_rounding(x):
	if x < 0:
		return 0
	if x > 1:
		return 1
	return x

f = open(sys.argv[1])
Header = f.readline()
assert Header.startswith("i\tx\ty\tS\tj")

Xs = []
Ys = []
Ss = []
Map_i_j = {}
Pairs = []
IsLoops = []

Counter = 0
while 1:
	Line = f.readline()
	if len(Line) == 0:
		break
	Fields = Line[:-1].split('\t')
	assert len(Fields) >= 5
	
	i = int(Fields[0])
	x = float(Fields[1])
	y = float(Fields[2])
	S = float(Fields[3])
	sj = Fields[4]
	IsLoop = None
	if sj == ".":
		j = None
	else:
		j = int(sj)
		Map_i_j[i] = j
		Map_i_j[j] = i
	
		if i < j:
			Pair = (i, j)
		else:
			Pair = (j, i)
		Pairs.append(Pair)

		if len(Fields) > 5:
			strIsLoop = Fields[5]
			if strIsLoop == "Rod":
				IsLoop = False
			elif strIsLoop == "Loop":
				IsLoop = True
			else:
				assert False

	assert i == Counter
	Counter += 1
	x = fix_rounding(x)
	y = fix_rounding(y)

	Xs.append(x)
	Ys.append(y)
	Ss.append(S)
	IsLoops.append(IsLoop)

GenomeLength = len(Xs)
RescaleToGenomeLength(GenomeLength)

FIG_WIDTH = CIRCLE_DIAMETER + 2*HORIZ_MARGIN
FIG_HEIGHT = CIRCLE_DIAMETER + 2*VERT_MARGIN

CIRCLE_BOUNDING_BOX_LEFT = HORIZ_MARGIN
CIRCLE_BOUNDING_BOX_TOP = VERT_MARGIN

print(r'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="%.6g" height="%.6g">' \
  % (FIG_WIDTH, FIG_HEIGHT))

PairCount = len(Pairs)
for PairIndex in range(0, PairCount):
# for PairIndex in [0, 50, 75, 120]:
	Pair = Pairs[PairIndex]
	i, j = Pair
	Xi = Xs[i]
	Yi = Ys[i]
	Xj = Xs[j]
	Yj = Ys[j]
	Si = Ss[i]
	Sj = Ss[j]
	IsLoop_i = IsLoops[i]
	IsLoop_j = IsLoops[j]
	IsLoop = IsLoop_i is True or IsLoop_j is True

	assert Si == Sj

	PLOT_Xi = CIRCLE_BOUNDING_BOX_LEFT + Xi*CIRCLE_DIAMETER
	PLOT_Yi = CIRCLE_BOUNDING_BOX_TOP + Yi*CIRCLE_DIAMETER

	PLOT_Xj = CIRCLE_BOUNDING_BOX_LEFT + Xj*CIRCLE_DIAMETER
	PLOT_Yj = CIRCLE_BOUNDING_BOX_TOP + Yj*CIRCLE_DIAMETER

	if Si < 0:
		Si = 0
	if Si > 1:
		Si = 1
	Color = GetColor(Si)
	
	if STYLE == "straightlines":
		print(r'<line x1="%.6g" y1="%.6g" x2="%.6g" y2="%.6g" stroke-width="%.6g" stroke="%s" />' \
		  % (PLOT_Xi, PLOT_Yi, PLOT_Xj, PLOT_Yj, LINE_WIDTH, Color))
	elif STYLE == "bezier":

		if FLARE != 0 and IsLoop:
			SavedBend = BEND
			BEND = -FLARE*BEND

		Handle_ix, Handle_iy, Handle_jx, Handle_jy = \
		  GetBezierHandleCoords(PLOT_Xi, PLOT_Yi, PLOT_Xj, PLOT_Yj)

		if FLARE != 0 and IsLoop:
			BEND = SavedBend

		print(r'<path d="M%.6g,%.6g C%.6g,%.6g %.6g,%.6g %.6g,%.6g" stroke-width="%.6g" fill="none" stroke="%s" />' \
		  % (PLOT_Xi, PLOT_Yi, Handle_ix, Handle_iy, Handle_jx, Handle_jy, PLOT_Xj, PLOT_Yj, LINE_WIDTH, Color))
	else:
		sys.stderr.write("Bad STYLE\n")
		assert False

if Title != None:
	print(r'<text x="3" y="14" font-family="sans-serif" font-size="12" fill="black" text-anchor="left">%s</text>' % Title)

print("</svg>")
