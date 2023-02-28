# For a known set of cartesian co-ordinates for the end effector, what are the necessary joint angles?
# As per https://appliedgo.net/roboticarm/

import math

# Lengths of each arm part
len1 = 10 
len2 = 10

#
def lawOfCosines(a, b, c): 
	return math.acos((a*a + b*b - c*c) / (2 * a * b))


def distance(x, y):
	return math.sqrt(x*x + y*y)

def angles(x, y):

    # First, get the length of line dist.	
	dist = distance(x, y)
    # Calculating angle D1 is trivial. Atan2 is a modified arctan() function that returns unambiguous results.	
	D1 = math.atan2(y, x)
    # D2 can be calculated using the law of cosines where a = dist, b = len1, and c = len2.	
	D2 = lawOfCosines(dist, len1, len2)
    # Then A1 is simply the sum of D1 and D2.	
	A1 = D1 + D2
    # A2 can also be calculated with the law of cosine, but this time with a = len1, b = len2, and c = dist.	
	A2 = lawOfCosines(len1, len2, dist)

	return A1, A2

def deg(rad):
	return rad * 180 / math.pi

print("Lets do some tests. First move to (5,5):")
x, y = 5, 5
a1, a2 = angles(x, y)
print("x=%v, y=%v: A1=%v (%v°), A2=%v (%v°)\n", x, y, a1, deg(a1), a2, deg(a2))

print("If y is 0 and x = Sqrt(10^2 + 10^2), then alpha should become 45 degrees and beta should become 90 degrees.")
x, y = math.sqrt(200), 0
a1, a2 = angles(x, y)
print("x=%v, y=%v: A1=%v (%v°), A2=%v (%v°)\n", x, y, a1, deg(a1), a2, deg(a2))

# fmt.Println("Now let's try moving to (1, 19).")
# x, y = 1, 19
# a1, a2 = angles(x, y)
# fmt.Printf("x=%v, y=%v: A1=%v (%v°), A2=%v (%v°)\n", x, y, a1, deg(a1), a2, deg(a2))

# fmt.Println("n extreme case: (20,0). The arm needs to stretch along the y axis.")
# x, y = 20, 0
# a1, a2 = angles(x, y)
# fmt.Printf("x=%v, y=%v: A1=%v (%v°), A2=%v (%v°)\n", x, y, a1, deg(a1), a2, deg(a2))

# fmt.Println("And (0,20).")
# x, y = 0, 20
# a1, a2 = angles(x, y)
# fmt.Printf("x=%v, y=%v: A1=%v (%v°), A2=%v (%v°)\n", x, y, a1, deg(a1), a2, deg(a2))

# fmt.Println("Moving to (0,0) technically works if the arm segments have the same length, and if the arm does not block itself. Still the result looks a bit weird!?")
# x, y = 0, 0
# a1, a2 = angles(x, y)
# fmt.Printf("x=%v, y=%v: A1=%v (%v°), A2=%v (%v°)\n", x, y, a1, deg(a1), a2, deg(a2))

# fmt.Println("What happens if the target point is outside the reach? Like (20,20).")
# x, y = 20, 20
# a1, a2 = angles(x, y)
# fmt.Printf("x=%v, y=%v: A1=%v (%v°), A2=%v (%v°)\n", x, y, a1, deg(a1), a2, deg(a2))
