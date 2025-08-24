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
    #norm = norm.reshape((3,-1)).T           ##CHECK!!!
    norm = norm.reshape((3,-1))
    norm = norm.swapaxes(0,1)
    ds = np.sqrt(1+n_x**2+n_y**2)               ##Jacobian
    ds = ds*(xv[0,1]-xv[0,0])*(yv[1,0]-yv[0,0]) ##to have units of m**2

    #plane_positions = apu.Quantity([xv.flatten(), yv.flatten(), z.flatten()]).T
    plane_positions = apu.Quantity([xv.flatten(), yv.flatten(), z.flatten()])
    plane_positions = plane_positions.swapaxes(0,1)
    ds =  ds.flatten()
    return plane_positions, norm, ds


def deformed_circular_reflector(xv, yv, r, params):
    plane_positions, norm, ds = deformed_plane(xv,yv,params)
    mask = (plane_positions[:,0]**2+plane_positions[:,1]**2)< r**2
    return plane_positions[mask,:], norm[mask,:], ds[mask]




def paraboloid_cartesian(xv, yv, focus, diameter):
    """
        z = x**2+y**2/(4f)
        The normal are toward the inside of the paraboloid
        ##the parametrization is not good, it looks weird
    """
    z = (xv**2+yv**2)/(4*focus)
    mask = xv**2+yv**2<(diameter/2)**2
    ##compute normal vectors
    nx = xv/2/focus
    ny = yv/2/focus
    norm = np.array((-nx, -ny, np.ones(nx.shape)))
    norm = norm/np.sum(norm**2, axis=0)
    #norm = norm.reshape((3,-1)).T           ##CHECK!!!
    norm = norm.reshape((3,-1))
    norm = norm.swapaxes(0,1)

    ds = np.sqrt(1+nx**2+ny**2)
    ds = ds*(xv[0,1]-xv[0,0])*(yv[1,0]-yv[0,0]) ##to have units of m**2
    surf_pos = apu.Quantity((xv.flatten(), yv.flatten(), z.flatten()))
    surf_pos = surf_pos.swapaxes(0,1)
    return surf_pos, norm, ds, mask


def paraboloid_cylindrical(rv, tv, focus, diameter): 
    #in cilindrical the parametrization is:
    ## R(r,theta) = (rcos(theat), rsin(theta), r/2f)
    ###The diameter here does nothing.. I should give that at the rv
    xv = rv*np.cos(tv)
    yv = rv*np.sin(tv)
    zv = rv**2/(4*focus)
    surf_pos = apu.Quantity([xv.flatten(),yv.flatten(),zv.flatten()]).T
    ##compute normal vectors
    ##The tangent vectors are then: dR/dr =     (cos(theta), sin(theta), 1/2f)
    ##                              dR/dtheta = (-rsin(theta), rcose(theta), 0)
    ##And to compute the normal vector we make dR/dr x dR/dtheta 
    ## N = (-r**2/2/f cos(theta), -r**2/2/f sin(theta), r)
    nx = -rv**2/2/focus*np.cos(tv)
    ny = -rv**2/2/focus*np.sin(tv)
    nz = rv
    norm = np.array((nx, ny, nz))
    norm = norm/np.sqrt(np.sum(norm**2, axis=0))
    norm = norm.reshape((3,-1)).T           ##CHECK!!!
    #norm = norm.reshape((3,-1))
    #norm = norm.swapaxes(0,1)

    #norm = apu.Quantity([nx.flatten(),ny.flatten(),nz.flatten()]).T
    #norm = norm/np.sqrt(np.sum(norm, axis=1))
    ##this one is just magnitude of the norm vector..
    ds = rv*np.sqrt(1+(rv/(2*focus))**2)*(rv[0,1]-rv[0,0])*(tv[1,0]-tv[0,0])
    ds = ds.flatten()
    return surf_pos, norm, ds



def hyperboloid_cylindrical(rv, tv, a,b):
    ### the hyperboloid points satisfy
    ### z(r) =  +-a*sqrt(r**2/b**2-1)
    ###
    xv = rv*np.cos(tv)
    yv = rv*np.sin(tv)
    zv = a*np.sqrt(1+rv**2/b**2)
    surf_pos = apu.Quantity([xv.flatten(),yv.flatten(),zv.flatten()]).T
    dz_dr = a*rv/(b**2*np.sqrt(1+rv**2/b**2))
    nx = -dz_dr*rv*np.cos(tv)/(np.sqrt(1+dz_dr))
    ny = -dz_dr*rv*np.sin(tv)/(np.sqrt(1+dz_dr))
    nz = 1/(np.sqrt(1+dz_dr))
    norm = np.array((nx,ny,nz)).T
    ds = rv*np.sqrt(1+dz_dr**2)*(rv[0,1]-rv[0,0])*(tv[1,0]-tv[0,0])
    ds = ds.flatten()
    return surf_pos, norm, ds




