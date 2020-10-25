import svgwrite
import numpy as np

ABBREVIATIONS = {
    "CP": "CPT -kairaus",
    "CP/CPT": "CPT -kairaus",
    "CPT": "CPT -kairaus",
    "CPTU": "CPTU -kairaus",
    "CU": "CPTU -kairaus",
    "CU/CPTU": "CPTU -kairaus",
    "FVT": "Siipikairaus",
    "HE": "Heijarikairaus",
    "HE/DP": "Heijarikairaus",
    "HK": "Heijarikairaus vääntömomentilla",
    "HK/DP": "Heijarikairaus vääntömomentilla",
    "HP": "Puristin-heijari -kairaus",
    "KE": "Kallionäytekairaus laajennettu",
    "KO": "Koekuoppa",
    "KR": "Kallionäytekairaus videoitu",
    "LB": "Laboratoriotutkimukset // Kallionäytetutkimus",
    "LY": "Lyöntikairaus",
    "MW": "MWD -kairaus",
    "NE": "Näytteenotto häiriintymätön",
    "NO": "Näytteenotto häiritty",
    "PA": "Painokairaus",
    "PA/WST": "Painokairaus",
    "PI": "Pistokairaus",
    "PMT": "Pressometrikoe",
    "PO": "Porakonekairaus",
    "PR": "Puristinkairaus",
    "PS": "Pressometrikoe",
    "PS/PMT": "Pressometrikoe",
    "PT": "Putkikairaus",
    "RK": "Rakeisuus",
    "SI": "Siipikairaus",
    "SI/FVT": "Siipikairaus",
    "TR": "Tärykairaus",
    "VK": "Vedenpinnan mittaus kaivosta",
    "VO": "Orsiveden mittausputki",
    "VP": "Pohjaveden mittausputki",
    "VPK": "Kalliopohjavesiputki",
    "WST": "Painokairaus",
    "Missing survey abbreviation": "Missing survey abbreviation",
}

DRAWING_SIZE = np.array([25.0, 25.0])
STROKE_WIDTH = 1


def getArc_com(p0, p1, radius, sweep=0):
    """Get arc command."""
    args = {
        "x0": p0[0],
        "y0": p0[1],
        "xradius": radius,
        "yradius": radius,
        "ellipseRotation": 0,  # has no effect for circles,
        "sweep": int(bool(sweep)),
        "x1": (p1[0] - p0[0]),
        "y1": (p1[1] - p0[1]),
    }
    return (
        "M %(x0)f,%(y0)f a %(xradius)f,%(yradius)f %(ellipseRotation)f 0,%(sweep)d %(x1)f,%(y1)f"
        % args
    )


def getArc(p0, p1, radius, width=3, stroke="black", fill="black", sweep=0):
    """Adds an arc that bulges to the right (sweep=0) or left (sweep=1)
    as it moves from p0 to p1"""
    d = getArc_com(p0, p1, radius, sweep=0)
    path = svgwrite.path.Path(
        d=d,
        fill=fill,
        stroke=stroke,
        stroke_width=width,
    )
    return path


def po_icon():
    dwg = svgwrite.Drawing(size=DRAWING_SIZE.tolist())
    radius = DRAWING_SIZE[0] / 2 - STROKE_WIDTH / 2
    shp = svgwrite.shapes.Circle(
        center=(DRAWING_SIZE / 2).tolist(),
        r=radius,
        fill="none",
        stroke="black",
        stroke_width=STROKE_WIDTH,
    )
    dwg.add(shp)
    return dwg


def tr_icon():
    dwg = svgwrite.Drawing(size=DRAWING_SIZE.tolist())
    radius = DRAWING_SIZE[0] / 2 - STROKE_WIDTH / 2
    shp = svgwrite.shapes.Circle(
        center=(DRAWING_SIZE / 2).tolist(),
        r=radius,
        fill="none",
        stroke="black",
        stroke_width=STROKE_WIDTH,
    )

    start = (DRAWING_SIZE[0] / 2, 0)
    end = (DRAWING_SIZE[0] / 2, DRAWING_SIZE[1])
    line1 = svgwrite.shapes.Line(start=start, end=end, stroke_width=STROKE_WIDTH, stroke="black")

    start = (0, DRAWING_SIZE[1] / 2)
    end = (DRAWING_SIZE[0], DRAWING_SIZE[1] / 2)
    line2 = svgwrite.shapes.Line(start=start, end=end, stroke_width=STROKE_WIDTH, stroke="black")

    dwg.add(line1)
    dwg.add(line2)
    dwg.add(shp)
    return dwg


def pa_icon():
    dwg = svgwrite.Drawing(size=DRAWING_SIZE.tolist())
    radius = DRAWING_SIZE[0] / 2 - STROKE_WIDTH / 2
    shp = svgwrite.shapes.Circle(
        center=(DRAWING_SIZE / 2).tolist(),
        r=radius,
        fill="none",
        stroke="black",
        stroke_width=STROKE_WIDTH,
    )

    arc = getArc(
        (0, DRAWING_SIZE[1] / 2),
        (DRAWING_SIZE[0], DRAWING_SIZE[1] / 2),
        radius=radius,
        width=0,
        stroke="none",
    )
    dwg.add(arc)
    dwg.add(shp)
    return dwg


def pr_icon():
    dwg = svgwrite.Drawing(size=DRAWING_SIZE.tolist())
    radius = DRAWING_SIZE[0] / 2  # - STROKE_WIDTH / 2
    # radius=1
    circle = svgwrite.shapes.Circle(
        center=(DRAWING_SIZE / 2).tolist(),
        r=radius,
        fill="none",
        stroke="black",
        stroke_width=STROKE_WIDTH,
    )
    # dwg.add(circle)  #Helper circle

    cos30 = 3 ** 0.5 / 2
    r = DRAWING_SIZE[0] / 2
    kolmion_sivu = cos30 * DRAWING_SIZE[0]
    p1 = (DRAWING_SIZE[0] / 2, DRAWING_SIZE[1])
    p2 = ((DRAWING_SIZE[0] - kolmion_sivu) / 2, DRAWING_SIZE[1] - 1.5 * r)
    p3 = (DRAWING_SIZE[0] - (DRAWING_SIZE[0] - kolmion_sivu) / 2, DRAWING_SIZE[1] - 1.5 * r)
    points = [p1, p2, p3]

    pl = svgwrite.shapes.Polygon(points, fill="none", stroke="black", stroke_width=STROKE_WIDTH)
    dwg.add(pl)
    dwg.attribs["height"] += STROKE_WIDTH
    return dwg


def hp_icon():
    dwg = svgwrite.Drawing(size=DRAWING_SIZE.tolist())
    cos30 = 3 ** 0.5 / 2
    r = DRAWING_SIZE[0] / 2
    kolmion_sivu = cos30 * DRAWING_SIZE[0]
    p1 = (DRAWING_SIZE[0] / 2, DRAWING_SIZE[1])
    p2 = ((DRAWING_SIZE[0] - kolmion_sivu) / 2, DRAWING_SIZE[1] - 1.5 * r)
    p3 = (DRAWING_SIZE[0] - (DRAWING_SIZE[0] - kolmion_sivu) / 2, DRAWING_SIZE[1] - 1.5 * r)
    points = [p1, p2, p3]

    pl = svgwrite.shapes.Polygon(points, fill="none", stroke="black", stroke_width=STROKE_WIDTH)
    dwg.add(pl)

    radius = cos30 * (kolmion_sivu / 3)
    circle = svgwrite.shapes.Circle(
        center=(DRAWING_SIZE / 2).tolist(),
        r=radius,
        fill="none",
        stroke="black",
        stroke_width=STROKE_WIDTH,
    )
    dwg.add(circle)

    p1 = (DRAWING_SIZE[0] / 2 - radius, DRAWING_SIZE[1] / 2)
    p2 = (DRAWING_SIZE[0] / 2, DRAWING_SIZE[1] / 2 - radius)
    arc = getArc(p2, p1, radius, width=1e-5, fill="black")
    p3 = (DRAWING_SIZE / 2).tolist()
    arc.push("L {} {}".format(p3[0], p3[1]))
    dwg.add(arc)
    dwg.attribs["height"] += STROKE_WIDTH
    return dwg


def he_icon():
    dwg = svgwrite.Drawing(size=DRAWING_SIZE.tolist())
    cos30 = 3 ** 0.5 / 2
    r = DRAWING_SIZE[0] / 2
    kolmion_sivu = cos30 * DRAWING_SIZE[0]
    p1 = (DRAWING_SIZE[0] / 2, DRAWING_SIZE[1])
    p2 = ((DRAWING_SIZE[0] - kolmion_sivu) / 2, DRAWING_SIZE[1] - 1.5 * r)
    p3 = (DRAWING_SIZE[0] - (DRAWING_SIZE[0] - kolmion_sivu) / 2, DRAWING_SIZE[1] - 1.5 * r)
    points = [p1, p2, p3]

    pl = svgwrite.shapes.Polygon(points, fill="none", stroke="black", stroke_width=STROKE_WIDTH)
    # dwg.add(pl)

    radius = DRAWING_SIZE[0] / 2 - STROKE_WIDTH
    circle = svgwrite.shapes.Circle(
        center=(DRAWING_SIZE / 2).tolist(),
        r=radius,
        fill="none",
        stroke="black",
        stroke_width=STROKE_WIDTH,
    )
    dwg.add(circle)

    p1 = (DRAWING_SIZE[0] / 2 - radius, DRAWING_SIZE[1] / 2)
    p2 = (DRAWING_SIZE[0] / 2, DRAWING_SIZE[1] / 2 - radius)
    arc = getArc(p2, p1, radius, width=1e-5, fill="black")
    p3 = (DRAWING_SIZE / 2).tolist()
    arc.push("L {} {}".format(p3[0], p3[1]))
    dwg.add(arc)
    return dwg


def pt_icon():
    dwg = svgwrite.Drawing(size=DRAWING_SIZE.tolist())
    cos30 = 3 ** 0.5 / 2
    r = DRAWING_SIZE[0] / 2
    kolmion_sivu = cos30 * DRAWING_SIZE[0]
    p1 = (DRAWING_SIZE[0] / 2, DRAWING_SIZE[1])
    p2 = ((DRAWING_SIZE[0] - kolmion_sivu) / 2, DRAWING_SIZE[1] - 1.5 * r)
    p3 = (DRAWING_SIZE[0] - (DRAWING_SIZE[0] - kolmion_sivu) / 2, DRAWING_SIZE[1] - 1.5 * r)
    points = [p1, p2, p3]

    pl = svgwrite.shapes.Polygon(points, fill="none", stroke="black", stroke_width=STROKE_WIDTH)
    dwg.add(pl)

    radius = cos30 * (kolmion_sivu / 3)
    circle = svgwrite.shapes.Circle(
        center=(DRAWING_SIZE / 2).tolist(),
        r=radius,
        fill="none",
        stroke="black",
        stroke_width=STROKE_WIDTH,
    )
    dwg.add(circle)

    dwg.attribs["height"] += STROKE_WIDTH
    return dwg


def si_icon():
    dwg = svgwrite.Drawing(size=DRAWING_SIZE.tolist())

    circle_shrink = 4 / 5
    radius = (DRAWING_SIZE[0] / 2) * circle_shrink
    circle = svgwrite.shapes.Circle(
        center=(DRAWING_SIZE / 2).tolist(),
        r=radius,
        fill="none",
        stroke="black",
        stroke_width=STROKE_WIDTH,
    )
    dwg.add(circle)

    dist_to_mid = (2 ** 0.5) * DRAWING_SIZE[0] / 2
    p1 = [0, 0]
    p2 = ((dist_to_mid - radius) / 2 ** 0.5, (dist_to_mid - radius) / 2 ** 0.5)
    points = [p1, p2]
    pl = svgwrite.shapes.Polygon(points, fill="none", stroke="black", stroke_width=STROKE_WIDTH)
    dwg.add(pl)

    p1 = [DRAWING_SIZE[0], 0]
    p2 = (DRAWING_SIZE[0] - (dist_to_mid - radius) / 2 ** 0.5, (dist_to_mid - radius) / 2 ** 0.5)
    points = [p1, p2]
    pl = svgwrite.shapes.Polygon(points, fill="none", stroke="black", stroke_width=STROKE_WIDTH)
    dwg.add(pl)

    p1 = [DRAWING_SIZE[0], DRAWING_SIZE[1]]
    p2 = (
        DRAWING_SIZE[0] - (dist_to_mid - radius) / 2 ** 0.5,
        DRAWING_SIZE[1] - (dist_to_mid - radius) / 2 ** 0.5,
    )
    points = [p1, p2]
    pl = svgwrite.shapes.Polygon(points, fill="none", stroke="black", stroke_width=STROKE_WIDTH)
    dwg.add(pl)

    p1 = [0, DRAWING_SIZE[1]]
    p2 = ((dist_to_mid - radius) / 2 ** 0.5, DRAWING_SIZE[1] - (dist_to_mid - radius) / 2 ** 0.5)
    points = [p1, p2]
    pl = svgwrite.shapes.Polygon(points, fill="none", stroke="black", stroke_width=STROKE_WIDTH)
    dwg.add(pl)

    # Note edge line cut off
    # dwg.attribs["height"] += STROKE_WIDTH
    # dwg.attribs["width"] += STROKE_WIDTH
    return dwg


def no_icon():
    figure_stretch = 1.5
    width = DRAWING_SIZE[0] * figure_stretch
    dwg = svgwrite.Drawing(size=(DRAWING_SIZE * figure_stretch).tolist())

    radius = (width / 2) - STROKE_WIDTH
    circle = svgwrite.shapes.Circle(
        center=(DRAWING_SIZE * figure_stretch / 2).tolist(),
        r=radius,
        fill="none",
        stroke="black",
        stroke_width=STROKE_WIDTH,
    )
    dwg.add(circle)

    circle_shrink = 3.5 / 5
    radius = (width / 2) * circle_shrink
    circle = svgwrite.shapes.Circle(
        center=(DRAWING_SIZE * figure_stretch / 2).tolist(),
        r=radius,
        fill="none",
        stroke="black",
        stroke_width=STROKE_WIDTH,
    )
    dwg.add(circle)
    return dwg


def ne_icon():
    figure_stretch = 1.5
    width = DRAWING_SIZE[0] * figure_stretch
    dwg = svgwrite.Drawing(size=(DRAWING_SIZE * figure_stretch).tolist())

    radius = (width / 2) - STROKE_WIDTH
    circle = svgwrite.shapes.Circle(
        center=(DRAWING_SIZE * figure_stretch / 2).tolist(),
        r=radius,
        fill="none",
        stroke="black",
        stroke_width=STROKE_WIDTH,
    )
    dwg.add(circle)

    circle_shrink = 3.5 / 5
    radius = (width / 2) * circle_shrink
    circle = svgwrite.shapes.Circle(
        center=(DRAWING_SIZE * figure_stretch / 2).tolist(),
        r=radius,
        fill="none",
        stroke="black",
        stroke_width=STROKE_WIDTH,
    )
    dwg.add(circle)

    p1 = [STROKE_WIDTH, width / 2]
    p2 = [width - STROKE_WIDTH, width / 2]
    arc = getArc(p1, p2, radius, width=1e-9, stroke="none", fill="black")

    p3 = (width / 2 + radius, width / 2)
    arc.push("L {} {}".format(p3[0], p3[1]))

    p4 = (width / 2 - radius, width / 2)
    arc_arg = getArc_com(p3, p4, radius, sweep=1)

    arc.push(arc_arg)
    dwg.add(arc)
    return dwg


def vo_icon():
    width = DRAWING_SIZE[0]
    height = DRAWING_SIZE[1] * 2
    dwg = svgwrite.Drawing(size=(width, height))

    radius1 = (width / 2) - STROKE_WIDTH
    center1 = (width / 2, 3 * height / 4)
    circle = svgwrite.shapes.Circle(
        center=center1,
        r=radius1,
        fill="none",
        stroke="black",
        stroke_width=STROKE_WIDTH,
    )
    dwg.add(circle)

    radius2 = (width / 2) * 0.30
    center2 = (width / 2, height / 4)
    circle = svgwrite.shapes.Circle(
        center=center2,
        r=radius2,
        fill="black",
        stroke="black",
        stroke_width=STROKE_WIDTH,
    )
    dwg.add(circle)

    p1 = (width / 2, center1[1] - radius1)
    p2 = (width / 2, center2[1] + radius2)
    line = svgwrite.shapes.Line(p1, p2, stroke="black", stroke_width=STROKE_WIDTH)
    dwg.add(line)
    # dwg.add(
    #    svgwrite.shapes.Circle((width / 2, height / 2), stroke="red", stroke_width=STROKE_WIDTH * 4)
    # )
    return dwg


def vp_icon():
    width = DRAWING_SIZE[0]
    height = DRAWING_SIZE[1] * 2
    dwg = svgwrite.Drawing(size=(width, height))

    radius1 = (width / 2) - STROKE_WIDTH
    center1 = (width / 2, 3 * height / 4)
    circle = svgwrite.shapes.Circle(
        center=center1,
        r=radius1,
        fill="none",
        stroke="black",
        stroke_width=STROKE_WIDTH,
    )
    dwg.add(circle)

    radius2 = (width / 2) * 0.30
    center2 = (width / 2, height / 4)
    circle = svgwrite.shapes.Circle(
        center=center2,
        r=radius2,
        fill="none",
        stroke="black",
        stroke_width=STROKE_WIDTH,
    )
    dwg.add(circle)

    p1 = (width / 2, center1[1] - radius1)
    p2 = (width / 2, center2[1] + radius2)
    line = svgwrite.shapes.Line(p1, p2, stroke="black", stroke_width=STROKE_WIDTH)
    dwg.add(line)
    # dwg.add(
    #    svgwrite.shapes.Circle((width / 2, height / 2), stroke="red", stroke_width=STROKE_WIDTH * 4)
    # )
    return dwg


FUNCTIONS = {
    # "CP": "CPT -kairaus",
    # "CP/CPT": "CPT -kairaus",
    # "CPT": "CPT -kairaus",
    # "CPTU": "CPTU -kairaus",
    # "CU": "CPTU -kairaus",
    # "CU/CPTU": "CPTU -kairaus",
    "FVT": si_icon,
    "HE": he_icon,
    "HE/DP": he_icon,
    "HK": he_icon,
    "HK/DP": he_icon,
    "HP": hp_icon,
    # "KE": "Kallionäytekairaus laajennettu",
    # "KO": "Koekuoppa",
    # "KR": "Kallionäytekairaus videoitu",
    # "LB": "Laboratoriotutkimukset // Kallionäytetutkimus",
    "LY": tr_icon,
    # "MW": "MWD -kairaus",
    "NE": ne_icon,
    "NO": no_icon,
    "PA": pa_icon,
    "PA/WST": pa_icon,
    "PI": tr_icon,
    # "PMT": "Pressometrikoe",
    "PO": po_icon,
    "PR": pr_icon,
    # "PS": "Pressometrikoe",
    # "PS/PMT": "Pressometrikoe",
    "PT": pt_icon,
    # "RK": "Rakeisuus",
    "SI": si_icon,
    "SI/FVT": si_icon,
    "TR": tr_icon,
    # "VK": "Vedenpinnan mittaus kaivosta",
    "VO": vo_icon,
    "VP": vp_icon,
    # "VPK": "Kalliopohjavesiputki",
    "WST": pa_icon,
    # "Missing survey abbreviation": "Missing survey abbreviation",
}

if __name__ == "__main__":
    print("Printing icons.")
    for abb in FUNCTIONS:
        f = FUNCTIONS[abb]
        name = ABBREVIATIONS[abb]
        icon = f()
        icon.saveas(abb.replace("/", "_") + ".svg")
        print(name, "saved.")

    #import os
    #import cairosvg
    #conda install cairo
    #pip install cairosvg
    #files = [i for i in os.listdir() if i.split(".")[-1] == "svg"]
    #for file in files:
    #    name_out = file.split(".")[0] + ".png"
    #    cairosvg.svg2png(url=file, write_to=name_out, dpi=600)
