import numpy as np
import matplotlib.pyplot as plt
from astropy import units as apu
from astropy import constants as cte
import ipdb



def deformed_plane(xv,yv, params):
    """
    Computes a deformed plane with the following deformations
    zv = a+bx+cy+d(x-y)+e(x+y)
    that is equivalent a change in the piston, tilt and a rotational deformation
    
    this function also return the normal vector of the plane and the surface element

    xv, yv: meshgrid with units of length
    params: [a,b,c,d,e] or [piston, x tilt, y tilt, deform 1, deform 2]
    """
    x = xv.to_value(apu.m)
    y = yv.to_value(apu.m)
    z = (params[0]+
         params[1]*x+
         params[2]*y+
         params[3]*(x**2+y**2)+
         params[4]*(x**2-y**2))*apu.m
    ##normal vector nx = dz/dx, ny=dz/dy
    n_x = params[1]+2*x*(params[3]+params[4])   
    n_y = params[2]+2*y*(params[3]-params[4])
    norm = np.array((-n_x, -n_y, np.ones(n_x.shape)))
    norm = norm/np.sqrt(np.sum(norm**2, axis=0))
    norm = norm.reshape((3,-1)).T           ##CHECK!!!
    ds = np.sqrt(1+n_x**2+n_y**2)               ##Jacobian
    ds = ds*(xv[0,1]-xv[0,0])*(yv[1,0]-yv[0,0]) ##to have units of m**2

    plane_positions = apu.Quantity([xv.flatten(), yv.flatten(), z.flatten()]).T
    ds =  ds.flatten()
    return plane_positions, norm, ds


def deformed_circular_reflector(xv, yv, r, params):
    plane_positions, norm, ds = deformed_plane(xv,yv,params)
    mask = (plane_positions[:,0]**2+plane_positions[:,1]**2)< r**2
    return plane_positions[mask,:], norm[mask,:], ds[mask]



