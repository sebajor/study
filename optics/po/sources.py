import numpy as np
from astropy import units as apu
from astropy import constants as cte
import ipdb


class plane_wave_source():
    ### 
    ###
    def __init__(self, 
                 freq, 
                 k_hat=np.array([0,0,1]), 
                 E0=np.array([1,0,0])*apu.V/apu.m, 
                 x0=np.zeros(3)*apu.m):
        """
        k_hat: kx,ky,kz  --> this should be normalized
        x0 = x0,y0,z0
        E0 = Ex, Ey, Ez

        The simplest is to take:
            k_vector = (0,0,1)
            x0 = (0,0,0)
            E0 = (E,0,0)
        btw, you have to ensure the orthogonality between E,H,k
        """
        wavel = cte.c/freq
        self.k_hat = k_hat
        self.k = 2*np.pi/wavel*k_hat
        self.r = x0
        self.E0 = E0

    def propagate(self, 
                  positions, 
                  eta = np.sqrt(cte.mu0/cte.eps0)
                  ):
        ###The positions (...,3)
        #ipdb.set_trace()
        R = positions-self.r[None, :]
        E = np.ones(positions.shape, dtype=complex)*self.E0[None,:]
        E = E*np.exp(-1j*np.sum(self.k*R, axis=1))[:,None]
        H = np.cross(self.k_hat[None, :], E)/eta
        return E, H
        




