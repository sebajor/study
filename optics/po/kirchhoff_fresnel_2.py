import numpy as np
import matplotlib.pyplot as plt
from astropy import units as apu
from astropy import constants as cte
import multiprocessing
import ipdb

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
        ##dont know why xiadong takes abs of this...
        aux = np.exp(-1j*k*r)/r*incident_E*cos_nr*ds
        E_out[i] = 1j/(wavelength)*np.sum(aux)
    return E_out


def kirchhoff_propagation_vector(surface_points, surface_normal, ds, incident_E, field_positions,
                                 wavelength):
    """
    This one uses numpy vectorization.. but as it generates multidimensional matrices needs a lot of
    memory..
    """
    k = 2*np.pi/wavelength
    R = field_positions[None,:,:]- surface_points[:,None,:]
    r = np.sqrt(np.sum(R**2, axis=2))
    R /= r[:,:,None]
    cos_nr = np.sum(surface_normal[:,None,:]*R, axis=-1)
    E_r = 1j/(wavelength)*np.sum(np.exp(-1j*k*r)/r*incident_E[:,None]*cos_nr*ds[:,None], axis=0)
    return E_r




def kf_worker(surface_points, surface_normal, ds, incident_E, field_positions,
              wavelength, k, indices, E_r, shape):
    E_r_local = np.frombuffer(E_r, dtype=np.complex128).reshape(shape)
    
    for i in indices:
        rx = field_positions[i,0]-surface_points[:,0]
        ry = field_positions[i,1]-surface_points[:,1]
        rz = field_positions[i,2]-surface_points[:,2]
        R = apu.Quantity([rx, ry, rz]).T
        r = np.sqrt(np.sum(R**2, axis=1))
        R_hat = R/r[:,None]
        
        cos_nr = np.sum(surface_normal*R_hat, axis=1)   ##dot product, the values should be normalized!
        aux = np.exp(-1j*k*r)/r*incident_E*cos_nr*ds
        ##write data out
        E_r_local[i] = (1j/(wavelength)*np.sum(aux)).to_value(apu.V/apu.m)


def kf_worker_vector(surface_points, surface_normal, ds, incident_E, field_positions,
                     wavelength, k, indices, E_r, shape):
    E_r_local = np.frombuffer(E_r, dtype=np.complex128).reshape(shape)
    R = field_positions[None,indices,:]- surface_points[:,None,:]
    r = np.sqrt(np.sum(R**2, axis=2))
    R /= r[:,:,None]
    cos_nr = np.sum(surface_normal[:,None,:]*R, axis=-1)
    E_r_local[indices] = (1j/(wavelength)*np.sum(np.exp(-1j*k*r)/r*incident_E[:,None]*cos_nr*ds[:,None], axis=0)).to_value(apu.V/apu.m)



def kirchhoff_propagation_batch(surface_points, surface_normal, ds, incident_E, field_positions,
                               wavelength, batch_size=32, max_threads=6, vector_worker=False):
    if(vector_worker):
        func = kf_worker_vector
    else:
        func = kf_worker
    k = 2*np.pi/wavelength
    shape = field_positions.shape[0]
    arr_shape = np.prod(shape)*2    
    E_r = multiprocessing.Array('d', int(arr_shape), lock=False)

    batches = field_positions.shape[0]//batch_size
    remains = field_positions.shape[0]%batch_size

    lock = 1
    workers = []
    i = 0

    while(i< batches):
        if(len(workers)< max_threads):
            indices = np.arange(batch_size)+batch_size*i
            proc = multiprocessing.Process(target=func,
                                           args=(surface_points, 
                                                 surface_normal,
                                                 ds, 
                                                 incident_E,
                                                 field_positions,
                                                 wavelength,
                                                 k,
                                                 indices,
                                                 E_r,
                                                 shape)
                                               )
            workers.append(proc)
            proc.start()
            i+=1
        else:
            for j in range(len(workers)):
                proc = workers.pop()
                try:
                    proc.join()
                except:
                    print("Error joining thread!")
    ##
    print("joining last threads")
    for j in range(len(workers)):
        proc = workers.pop()
        try:
            proc.join()
        except:
            print("Error joining thread!")
    print("All threads joined")
    if(remains !=0):
        print("running the remained part")
        indices = np.arange(remains)+batch_size*i
        func(surface_points, surface_normal, ds,incident_E,field_positions,
                    wavelength, k,indices, E_r, shape)
        ##finally we re-interpret once again the arrays
    #E_r = np.frombuffer(E_r.get_obj(), dtype=np.complex128).reshape(shape)
    #H_r = np.frombuffer(H_r.get_obj(), dtype=np.complex128).reshape(shape)
    E_r = np.frombuffer(E_r, dtype=np.complex128).reshape(shape)*apu.V/apu.m
    return E_r




