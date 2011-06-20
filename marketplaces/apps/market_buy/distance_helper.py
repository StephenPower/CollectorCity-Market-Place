import math

def distance_between_points(point1, point2, system="miles"):

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    lat1, long1 = point1
    lat2, long2 = point2
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    try:
        arc = math.acos( cos )
    except ValueError:
        #distance is too close
        return 0

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    if system == "miles":    
        earth_radious = 3959 #MILES
    else:
        earth_radious = 6378 #KILOMETERS
    return arc * earth_radious
