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
    k = 2*np.pi/wavelength
    E_out = np.zeros(field_positions.shape[0], dtype=complex)*apu.V/apu.m
    R = np.zeros(surface_points.shape)*apu.m
    for i in range(field_positions.shape[0]):
        R[:,0] = field_positions[i,0]-surface_points[:,0]
        R[:,1] = field_positions[i,1]-surface_points[:,1]
        R[:,2] = field_positions[i,2]-surface_points[:,2]
        
        r = np.sqrt(np.sum(R**2, axis=1))
        R_hat = R/r[:,None]
        
        cos_nr = np.sum(surface_normal*R_hat, axis=1)   ##dot product, the values should be normalized!
        aux = np.exp(-1j*k*r)/r*incident_E*cos_nr*ds
        E_out[i] = -1j/(wavelength)*np.sum(aux)
    return E_out


def kirchhoff_propagation_vector(surface_points, surface_normal, ds, incident_E, field_positions,
                                 wavelength):
    ##this one uses a lot of memory
    k = 2*np.pi/wavelength
    R = field_positions[None,:,:]- surface_points[:,None,:]
    r = np.sqrt(np.sum(R**2, axis=2))
    R /= r[:,:,None]
    cos_nr = np.sum(surface_normal[:,None,:]*R, axis=-1)
    E_r = -1j/(wavelength)*np.sum(np.exp(-1j*k*r)/r*incident_E[:,None]*cos_nr*ds[:,None], axis=0)
    ##add a minus for consistence with PO
    E_r *=-1
    return E_r












