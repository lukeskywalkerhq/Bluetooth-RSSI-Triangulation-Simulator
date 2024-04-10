import math
import random
import pygame
import pygame.event

# Global Variables
screenSize = [1000, 1000]
bounding = 300
baseStations = 3
randomness = 50
locations = []
intersections = []

pygame.init()
font = pygame.font.Font(None, 36)

# Set up the drawing window
screen = pygame.display.set_mode(screenSize)
clock = pygame.time.Clock()


# point Class
class Point:
    def __init__(self, location):
        self.location = location

        try:
            self.rssi = getRandomDistance(locations[0].location, location)
        except IndexError:
            self.rssi = 0

    def update_distance(self):
        try:
            self.rssi = getRandomDistance(locations[0].location, self.location)
        except IndexError:
            self.rssi = 0

    def update_location(self, location):
        self.location = location


# takes a list of points and finds the center (avg) of all points
def avg_points(points):
    sum_x = 0
    sum_y = 0

    for point in points:
        sum_x += point[0]
        sum_y += point[1]

    # Calculate the average of x and y coordinates
    avg_x = sum_x / len(points)
    avg_y = sum_y / len(points)

    return avg_x, avg_y


# takes in the number of base stations
# then compares the 2 intersection points of two circles, and compares them to all other points
# it then adds the point with the smallest distance to a list
# touch points of two circles are automatically added as there is only 1 point
def estimate_location(base):
    points = []
    for index in range(base):
        d1 = 0
        d2 = 0

        # checks to see if value is a pair of points (intersection) or a single point (touch)
        if isinstance(intersections[index][0], tuple):
            for j in range(base):
                if isinstance(intersections[j][0], tuple):
                    # Compare points to all other intersection points
                    d1 += getDistance(intersections[index][0], intersections[j][0])
                    d1 += getDistance(intersections[index][0], intersections[j][1])

                    d2 += getDistance(intersections[index][1], intersections[j][0])
                    d2 += getDistance(intersections[index][1], intersections[j][1])
                else:
                    # Compare points to touch points
                    d1 += getDistance(intersections[index][0], intersections[j])
                    d2 += getDistance(intersections[index][1], intersections[j])

            # added smallest to list
            if d1 < d2:
                points.append(intersections[index][0])
                pygame.draw.circle(screen, (255, 0, 0), intersections[index][0], 5)
            else:
                points.append(intersections[index][1])
                pygame.draw.circle(screen, (255, 0, 0), intersections[index][1], 5)
        else:
            # touch points added to list
            points.append(intersections[index])
            pygame.draw.circle(screen, (255, 0, 0), intersections[index], 5)

    return avg_points(points)


# locates touch point where 2 circles are outside oo
def single_point_touch_outside(x1, y1, r1, x2, y2, r2):
    touch_x = x1 + (x2 - x1) * r1 / (r1 + r2)
    touch_y = y1 + (y2 - y1) * r1 / (r1 + r2)
    return touch_x, touch_y


# locates touch point when 1 circle is inside a bigger one (o)
def single_point_touch_inside(x1, y1, r1, x2, y2):
    # Calculate the direction vector from (x1, y1) to (x2, y2)
    dx = x2 - x1
    dy = y2 - y1

    # Normalize the direction vector
    length = math.sqrt(dx ** 2 + dy ** 2)
    dx /= length
    dy /= length

    # Calculate the coordinates of the touch point as the midpoint of the segment
    touch_x = x1 + (r1 * dx)
    touch_y = y1 + (r1 * dy)
    return touch_x, touch_y


# determines if circles touch or not
# if not it expands/shrinks circles to touch in middle
# then if they touch then find tough points
# else find the intersection points
def find_circle_intersection(circle1, circle2):
    x1, y1, r1 = circle1
    x2, y2, r2 = circle2

    # Calculate the distance between the centers of the circles
    d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    # Check if the circles are too far apart or coincide
    if d > (r1 + r2):
        # Calculate the required radius to make the circles intersect
        old = r1
        r1 += (d - (r1 + r2)) / 2
        r2 += (d - (old + r2)) / 2
        pygame.draw.circle(screen, (0, 0, 255), (x1, y1), r1, 3)
        pygame.draw.circle(screen, (0, 0, 255), (x2, y2), r2, 3)
        return single_point_touch_outside(x1, y1, r1, x2, y2, r2)

    # see if r2 is inside r1
    if r1 > d + r2:
        old = r1
        r1 = r1 - (r1 - (d + r2)) / 2
        r2 = (old - (d - r2)) / 2
        pygame.draw.circle(screen, (0, 0, 255), (x1, y1), r1, 3)
        pygame.draw.circle(screen, (0, 0, 255), (x2, y2), r2, 3)
        return single_point_touch_inside(x1, y1, r1, x2, y2)

    # see if r1 is inside r2
    if r2 > (d + r1):
        old = r2
        r2 = r2 - (r2 - (d + r1)) / 2
        r1 = (old - (d - r1)) / 2
        pygame.draw.circle(screen, (0, 0, 255), (x1, y1), r1, 3)
        pygame.draw.circle(screen, (0, 0, 255), (x2, y2), r2, 3)
        return single_point_touch_inside(x2, y2, r2, x1, y1)

    # Calculate the intersection points
    a = (r1 ** 2 - r2 ** 2 + d ** 2) / (2 * d)
    h = math.sqrt(r1 ** 2 - a ** 2)
    x3 = x1 + a * (x2 - x1) / d
    y3 = y1 + a * (y2 - y1) / d

    # Calculate intersection points
    intersection_x1 = x3 + h * (y2 - y1) / d
    intersection_y1 = y3 - h * (x2 - x1) / d
    intersection_x2 = x3 - h * (y2 - y1) / d
    intersection_y2 = y3 + h * (x2 - x1) / d

    return (intersection_x1, intersection_y1), (intersection_x2, intersection_y2)


# calculates distance of 2 points
def getDistance(p1, p2):
    distance = math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2)
    if distance < 0:
        distance = distance * -1
    distance = math.sqrt(distance)
    return distance


# randomize the distance without going into negatives
# used to simulate inaccurate of bluetooth RSSI sensor
def getRandomDistance(p1, p2):
    distance = getDistance(p1, p2)
    randomAmount = random.randrange(-randomness, randomness)
    if distance + randomAmount < 0:
        distance = distance - randomAmount
    else:
        distance += randomAmount

    return distance


# generates a random point away from the edge of the screen
def randomPoint():
    location = random.randrange(0 + bounding, screenSize[0] - bounding), \
               random.randrange(0 + bounding, screenSize[1] - bounding)

    return Point(location)


# creates a list of random points
def setPoints():
    locations.clear()
    for i in range(baseStations + 1):
        locations.append(randomPoint())


# creates a label for points
def label(string, location):
    pygame.draw.rect(screen, (0, 0, 0), [location[0] - 10, location[1] - 35, 20, 20])
    text_surface = font.render(string, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.center = (location[0], location[1] - 25)
    screen.blit(text_surface, text_rect)


# Run until the user asks to quit
running = True
setPoints()

# bluetooth sensor does not update rapidly
# this simulates delay time of sesnor
TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 1000)

while running:
    clock.tick(30)  # limit frame rate
    screen.fill("black")  # wipe screen
    intersections.clear()

    # draw background distance circles for points
    for i in range(baseStations):
        pygame.draw.circle(screen, (0, 75, 0), locations[i + 1].location, locations[i + 1].rssi)

    # draw black outlines for distance circles
    for i in range(baseStations):
        pygame.draw.circle(screen, (0, 0, 0), locations[i + 1].location, locations[i + 1].rssi, 3)

    # get list of all intersections
    for i in range(1, baseStations + 1):
        for j in range(i, baseStations + 1):
            if i != j:
                circle1 = locations[i].location[0], locations[i].location[1], locations[i].rssi
                circle2 = locations[j].location[0], locations[j].location[1], locations[j].rssi
                intersections.append(find_circle_intersection(circle1, circle2))

    # draw and label all basestations
    for i in range(baseStations):
        pygame.draw.circle(screen, (0, 0, 0), locations[i + 1].location, 3)
        label(str(i + 1), locations[i + 1].location)

    # get estimated location
    estimate = estimate_location(baseStations)

    # draw line from estimated to Actual location
    pygame.draw.line(screen, (255, 255, 255), estimate, locations[0].location, 1)
    label(str(getDistance(estimate, locations[0].location)), screenSize)

    # draw estimated location
    pygame.draw.circle(screen, (255, 255, 255), estimate, 5)
    pygame.draw.circle(screen, (0, 0, 0), estimate, 3)
    label("E", estimate)

    # draw actual location
    pygame.draw.circle(screen, (255, 255, 255), locations[0].location, 5)
    pygame.draw.circle(screen, (0, 0, 0), locations[0].location, 3)
    label("B", locations[0].location)

    keys = pygame.key.get_pressed()

    # pygame even handels
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == TIMER_EVENT:
            for i in range(baseStations):
                locations[i + 1].update_distance()
            print(getDistance(locations[0].location, estimate))

    # if r is pressed randomize location of base-stations and beacon
    if keys[pygame.K_r]:
        setPoints()

    # move beacon location
    dx = (keys[pygame.K_d] - keys[pygame.K_a]) * 2
    dy = (keys[pygame.K_s] - keys[pygame.K_w]) * 2

    locations[0].update_location((locations[0].location[0] + dx, locations[0].location[1] + dy))

    pygame.display.flip()

# Done! Time to quit.
pygame.quit()
