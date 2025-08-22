import numpy as np
import matplotlib.pyplot as plt
from astropy import units as apu
from astropy import constants as cte

###
### The kirchhoff fresnel integral is an improvement over the geometrical optics
### since its equivalent to the Hyugenss-Fresnel interpretation.. where when given
### an aperture each point in the aperture generates spherical waves and the 
### field value at the point P will be the sum of all the waves
###
### E(P) = -i*k/(4*pi)*integral(E(r')exp(i*k*(r+s))/(r*s)*(cos(n,s)-cos(n,r))dS
###
### Where 
###     r       :   is the distance from the source to the aperture
###     s       :   is the distnace from the aperture to point P
###     cos(n,s):   is the cos angle between the unit vectors n and s--> ie dot(n,s)/|s|
###     cos(n,r):   cos angle between n and r 
### 
### The standard formalism assume a that the source are localized.. since in principle
### we can compute the fields at the aperture we can reduce the equation to:
###
### E(r) = -i*k/(4*pi)*integral(E(r')exp(i*k*|r-r'|)/|r-r'| *cos(n,r) dS    --> Hyuggens-Fresnel
###
### This method does not compute the currents over the surface, ie the reflections 
### are geometrical-like but they are waves are spherical and interfer between them
### This also implies that the results are always scalar only.



def kirchhoff_propagation(surface_points, surface_normal, ds, incident_E, field_positions,
                          wavelength):

