from geopy.distance import geodesic

def genCenters(x_min, y_min, x_max, y_max, precision):
    side = (x_max-x_min) / precision
    
    x_vals = []
    y_vals = []
    vals = []
    for x in range(10):
        if x==0:
            x_vals.append(x_min + side/2)
            continue
        x_vals.append(x_vals[-1] + side)

    for x in range(10):
        if x==0:
            y_vals.append(y_min + side/2)
            continue
        y_vals.append(y_vals[-1] + side)

    for x in x_vals:
        for y in y_vals:
            vals.append(( round(x, 5), round(y, 5) ))
    return vals


# start = (-25.7975, 37.8645)
# end   = (-25.7975, 37.8655)
# step  = 5
def move_boat(start, end, step):
    x_displacement = round(end[0] - start[0],5)
    y_displacement = round(end[1] - start[1],5)
    # print("Moving", x_displacement, "in x axis and", y_displacement, "in y axis" )
    x_step = x_displacement/step
    y_step = y_displacement/step
    crds = []
    new_x = start[0]
    new_y = start[1]

    #does not include starting position coordinates
    for i in range (step):
        new_x += x_step
        new_y += y_step
        crds.append((new_x, new_y))

    #print(crds)
    return crds



zone = [(37.87400, -25.78800), (37.87400, -25.79800), (37.8640, -25.79800), (37.86400, -25.78800)]
min_tuple = min(zone, key=lambda tup: tup[1]+tup[0])
max_tuple = max(zone, key=lambda tup: tup[1]+tup[0])

centers = genCenters(min_tuple[1], min_tuple[0], max_tuple[1], max_tuple[0], 10)
start_point = centers[0]
b = centers
centers.remove(start_point)

for x in b:
    print(x)
print(geodesic(b[0], b[1]).m)

closest = min(centers, key=lambda curr: geodesic(start_point, curr).m)
print(start_point)
print(closest)
print(geodesic(start_point, closest).m)


