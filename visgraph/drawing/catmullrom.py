
def spline4p(t, p_1, p0, p1, p2):
    x_1a = t * ((2-t) * t - 1) * p_1[0]
    x_1b = t * ((2-t) * t - 1) * p_1[1]

    x0a  = (t * t * (3 * t - 5) + 2) * p0[0]
    x0b  = (t * t * (3 * t - 5) + 2) * p0[1]

    x1a  = t * ((4 - 3 * t) * t + 1) * p1[0]
    x1b  = t * ((4 - 3 * t) * t + 1) * p1[1]

    x2a  = (t - 1) * t * t * p2[0]
    x2b  = (t - 1) * t * t * p2[1]

    final = ( (x_1a + x0a + x1a + x2a) / 2,
              (x_1b + x0b + x1b + x2b) / 2)

    return final

def calculate_catmullrom(points, steps = 30):
    ret = []
    percents = [ step / float(steps) for step in range(steps) ]
    for i in range(1, len(points) - 2):
        for t in percents:
            ret.append(spline4p(t, points[i-1], points[i], points[i+1], points[i+2]))
    return ret
