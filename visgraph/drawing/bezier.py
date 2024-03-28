def splitline(pt1, pt2, percent=0.5):
    '''
    Return a point which splits the given line at the
    given percentage...

    Example: splitline( (0,0), (20, 30), 0.1)
    '''

    pt1_x, pt1_y = pt1
    pt2_x, pt2_y = pt2

    deltax = (pt2_x - pt1_x) * percent
    deltay = (pt2_y - pt1_y) * percent

    return int(pt1_x + deltax), int(pt1_y + deltay)

def calculate_bezier(points, steps = 30):
    '''
    Arbitrary depth and arbitrary precision bezier implementation.  Takes
    a list of (x,y) point tuples and returnes the points to draw for the
    bezier curve.
    '''
    ret = []
    points = [ (float(x),float(y)) for x,y in points ]

    for i in range(steps+1):

        pcent = i / float(steps)

        layers = [ points, ]
        while len(layers[-1]) != 1:
            l_points = layers[-1]
            newpoints = [ splitline( l_points[i], l_points[i+1], pcent) for i in range(len(l_points)-1) ]
            layers.append(newpoints)

        ret.append(layers[-1][0])

    return ret
