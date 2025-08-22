import numpy as np
import matplotlib.pyplot as plt
from astropy import units as apu
from astropy import constants as cte
import ipdb




#I define this plane where the fields will be scatter

def deformed_plane(xv,yv, 
                params
                   ):
    """
    Generate a deformed plane with the given values, 
    TODO: We will need to return the normal vector of each point
    """
    ###
    ###
    x = xv.to_value(apu.m)
    y = yv.to_value(apu.m)
    z = (params[0]+
         params[1]*x+
         params[2]*y+
         params[3]*(x**2+y**2)+
         params[4]*(x**2-y**2))*apu.m
    
    ##If I mount this on other structure, like in a hyperbola I would need
    ##to modify the resulting normal vectors
    n_x = params[1]+2*x*(params[3]+params[4])
    n_y = params[2]+2*y*(params[3]-params[4])
    norm = np.array((-n_x, -n_y, np.ones(n_x.shape)))
    norm = norm/np.sqrt(np.sum(norm**2, axis=0))
    ##We also need to return the dS 
    ds = np.sqrt(1+n_x**2+n_y**2)
    ds = ds*(xv[0,1]-xv[0,0])*(yv[1,0]-yv[0,0]) ##to have units of m**2
    return z, norm, ds



def illum_gauss(xv, yv, I_coeff, pr):
    i_amp, c_dB = I_coeff[:2]
    x0, y0 = I_coeff[-2:]

    # workaround for units
    if type(c_dB) == apu.quantity.Quantity:
        sigma = 10 ** (c_dB / 20. / apu.dB)
    else:
        sigma = 10 ** (c_dB / 20.)
    if type(x0) != apu.quantity.Quantity:
        x0 *= apu.m
    if type(y0) != apu.quantity.Quantity:
        y0 *= apu.m

    Ea = (
        i_amp * np.sqrt(2 * np.pi * sigma ** 2) *
        np.exp(-((xv - x0) ** 2 + (yv - y0) ** 2) / (2 * (sigma * pr) ** 2))
        ).value
    return Ea


class gauss_source():

    def __init__(self, xv,yv,z, I_coeff,pr, 
                 freq, 
                 k_direction=np.array([0,0,1]),
                 e_pol=np.array([1,0,0])):
        self.pos0 = np.array((xv,yv,np.ones(xv.shape)*z))
        self.wavel = cte.c/freq
        self.k_direction = k_direction
        
        self.k = k_direction*2*np.pi/self.wavel
        e = illum_gauss(xv,yv,I_coeff, pr)
        self.e_pol = e_pol
        self.E_0 = e
        self.h_pol = np.cross(e_pol, self.k_direction)

    def get_H(self, E):
        eta0 = np.sqrt(cte.mu0/cte.eps0)
        self.H = E/eta0*self.h_pol

    def angular_spectrum_propagation(self, new_position):
        ##
        ##  new position is (x,y,z)
        ###
        dx = self.pos0[0,0,1]-self.pos0[0,0,0]
        dy = self.pos0[1,1,0]-self.pos0[1,0,0]

        u,v = np.fft.fftfreq(self.pos0.shape[2], dx), np.fft.fftfreq(self.pos0.shape[1], dy)
        uv, vv = np.meshgrid(u,v)
        
        kx = 2*np.pi*uv/apu.m
        ky = 2*np.pi*vv/apu.m

        kz_2 = (2*np.pi/self.wavel)**2-kx**2-ky**2
        kz = np.sqrt(kz_2, dtype=complex)

        ##now we move get the phase for any random position
        phase = kx*new_position[0]+ky*new_position[1]+kz*new_position[2]
        H = np.exp(1j*phase*np.sqrt(np.sum(new_position.to_value(apu.m)**2)))
        ##forward FFT
        e0_f =np.fft.fft2(self.E_0) ##here I got an issue.. 
        e0_f = e0_f*H
        e_d = np.fft.ifft2(e0_f)
        return e_d



class PO_Field():

    def __init__(self, positions, E, H, wavel):
        ## poisitions are of size (..,3) where each of the 3 indices represent the axis x,y,z
        ## Idem E, H have 3 components
        self.E = E
        self.H = H
        self.positions = positions
        self.wavel = wavel
        self.k = 2*np.pi/wavel

    def induce_field(self, face_positions, surf_normal, ds, new_positions, currents=False):
        ## dS = J *dx*dy --> ie should have L**2 units
        ## the face positions and the surf_normal should be the same points as E-H fields!
        ## new positions are the positions were the reflected fields are computed
        Je = 2*np.cross(surf_normal, self.H) 

        ##
        E = np.zeros(new_positions.shape, dtype=complex)*apu.V/apu.m
        H = np.zeros(new_positions.shape, dtype=complex)*apu.A/apu.m
        
        ##In the nomenclature r=new_positiosn, r'=face_positions
        ##

        R = np.zeros((face_positions.shape[0], 3))*apu.m
        for i in range(new_positions.shape[0]):
            ##For GPU usage its better to define R inside the loop!
            print("{:.4f}".format(100*i/new_positions.shape[0]))
            R[:,0] = new_positions[i,0]-face_positions[:,0]
            R[:,1] = new_positions[i,1]-face_positions[:,1]
            R[:,2] = new_positions[i,2]-face_positions[:,2]
            r = np.sqrt(np.sum(R**2, axis=1))
            R_hat = R/r[:,None]
            ##
            phase = self.k*r
            r2 = self.k**2*r**2
            r3 = self.k**3*r**3

            ##This shit is full of [:,None] bcs I need to match the dimensions and it seems that 
            ##that way avoid to copy data
            aux0 = Je*(-1j/phase[:, None]-1/r2[:, None]+1j/r3[:,None])
            aux1 = (np.sum(Je*R_hat, axis=1)[:,None]*R_hat)*(1j/phase[:,None]+3/r2[:,None]-3*1j/r3[:,None])
            ee = (np.exp(-1j*phase)[:,None]*self.k**2)*(aux0+aux1)*ds[:,None]
            E[i,:] = np.sum(ee, axis=0)/(4*np.pi)*np.sqrt(cte.mu0/cte.eps0)
            ###
            aux0 = np.cross(Je, R_hat)
            aux1 = (1+1j*phase)/r2
            he = (np.exp(-1j*phase)*self.k**2)[:,None]*aux0*aux1[:,None]*ds[:,None]
            H[i,:]=np.sum(he, axis=0)/(4*np.pi)# *np.sqrt(cte.eps0/cte.mu0) ##for what I got I dont need to multiply for the 1/eta0
            ##Xiadong have this...
            #aux1 = (R_hat/r2[:,None])*(1+1j*phase)[:,None]
            #he = (np.exp(-1j*phase)*self.k**2)[:,None]*aux0*aux1*ds[:,None]*dx*dy
            #H[i,:]=np.sum(he, axis=0)/(4*np.pi)*np.sqrt(cte.eps0/cte.mu0)
        if(currents):
            return PO_Field(new_positions, E,H, self.wavel), Je
        return PO_Field(new_positions, E,H, self.wavel)







##Ill create a plane in the z=3 and illuminate it with the propagagated beam
freq = 100*apu.GHz
wavel = cte.c/freq
prop_distance = wavel.to_value(apu.m)*2#*20     ##this is the offset of the 

params = np.zeros(5)
params[0] = prop_distance
add_params = np.random.random(4)*1e-2
#params[1:] += add_params

#scatter distance to evaluate
scatter_dist = 100*wavel.to_value(apu.m)#0.2#0.8#0.8*apu.m
scatter_size = 3

sampling = 128
plane_size = 1

x_plane = np.linspace(-plane_size/2,plane_size/2,sampling)*apu.m
xv_p, yv_p = np.meshgrid(x_plane, x_plane)
zv_p, n, ds = deformed_plane(xv_p, yv_p, params)

#circular surface
mask = (xv_p**2+yv_p**2)<((plane_size/2*apu.m)**2)
#mask = np.ones(xv_p.shape, dtype=bool)
xv_p = xv_p[mask]
yv_p = yv_p[mask]
zv_p = zv_p[mask]
ds = ds[mask]
n = n[:,mask]



##For some reason when composing the array it strips the unit...
surf_positions = np.array([xv_p.flatten(), yv_p.flatten(), zv_p.flatten()]).T*apu.m 
n = n.reshape((3,-1)).T 
##Since I put the feed in 0 I need the n to point at -
n = -n
ds = ds.flatten()

##

##gaussian beam
x = np.linspace(1,-1,sampling)*apu.m
xv,yv = np.meshgrid(x,x)
I_coeff = [1,10*apu.dB, 0*apu.m,0*apu.m]
feed = gauss_source(xv,yv,z=0,I_coeff=I_coeff, pr=0.1*apu.m, 
                    freq=freq)

##Here I propagate the feed field to the test surface
### E has units of V/m and H A/m


propagated_beam = feed.angular_spectrum_propagation([0,0, prop_distance]*apu.m)
#test
propagated_beam = np.abs(propagated_beam)
#E_i = np.zeros((propagated_beam.shape[0]*propagated_beam.shape[1], 3), dtype=complex)
E_i = np.zeros((xv_p.shape[0], 3), dtype=complex)*apu.V/apu.m
#gaussian
#E_i[:,0] = propagated_beam[mask]
#plane
E_i[:,0] = 1*apu.V/apu.m


eta0 = np.sqrt(cte.mu0/cte.eps0)
#H_i = np.zeros((propagated_beam.shape[0]*propagated_beam.shape[1], 3), dtype=complex)*apu.A/apu.m
H_i = np.zeros((xv_p.shape[0], 3), dtype=complex)
##gaussian
#H_i[:,1] = propagated_beam[mask]
#plane
H_i[:,1] = 1
H_i = H_i*apu.V/apu.m/eta0

#field_positions = np.array([xv.flatten(), yv.flatten(), np.ones(xv.shape[0]*xv.shape[1])*prop_distance*apu.m])
field_positions = np.array([xv_p.flatten(), yv_p.flatten(), np.ones(xv_p.shape[0])*prop_distance])*apu.m
field_positions = field_positions.T


x_new = np.linspace(-scatter_size/2,scatter_size/2,sampling)*apu.m
xv_new, yv_new = np.meshgrid(x_new, x_new)
new_pos = np.array((xv_new.flatten(), yv_new.flatten(), scatter_dist*np.ones(xv.flatten().shape))).T*apu.m


"""

#now I should be able to compute the inducend currents
input_field = PO_Field(field_positions, E_i, H_i, wavel)

#new_pos = np.array((xv.flatten(), yv.flatten(), scatter_dist*np.ones(xv.flatten().shape))).T*apu.m


out_field, Je = input_field.induce_field(surf_positions, n, ds, new_pos, currents=True)


E = out_field.E.reshape((sampling,sampling,3))
H = out_field.H.reshape((sampling,sampling,3))


##some plots

fig, axes = plt.subplots(2,3)
axes[0,0].pcolormesh(xv_new.to_value(apu.m), yv_new.to_value(apu.m), np.abs(E[:,:,0]))
axes[0,1].pcolormesh(xv_new.to_value(apu.m), yv_new.to_value(apu.m), np.abs(E[:,:,1]))
axes[0,2].pcolormesh(xv_new.to_value(apu.m), yv_new.to_value(apu.m), np.abs(E[:,:,2]))

axes[1,0].pcolormesh(xv_new.to_value(apu.m), yv_new.to_value(apu.m), np.angle(E[:,:,0]))
axes[1,1].pcolormesh(xv_new.to_value(apu.m), yv_new.to_value(apu.m), np.angle(E[:,:,1]))
axes[1,2].pcolormesh(xv_new.to_value(apu.m), yv_new.to_value(apu.m), np.angle(E[:,:,2]))

axes[0,0].set_title("$E_x$")
axes[0,1].set_title("$E_y$")
axes[0,2].set_title("$E_z$")

fig.suptitle("Plane at z={:.2f}$\lambda$".format(scatter_dist/wavel.to_value(apu.m)))


fig, axes = plt.subplots(2,3)
axes[0,0].pcolormesh(xv_new.to_value(apu.m), yv_new.to_value(apu.m), np.abs(H[:,:,0]))
axes[0,1].pcolormesh(xv_new.to_value(apu.m), yv_new.to_value(apu.m), np.abs(H[:,:,1]))
axes[0,2].pcolormesh(xv_new.to_value(apu.m), yv_new.to_value(apu.m), np.abs(H[:,:,2]))

axes[1,0].pcolormesh(xv_new.to_value(apu.m), yv_new.to_value(apu.m), np.angle(H[:,:,0]))
axes[1,1].pcolormesh(xv_new.to_value(apu.m), yv_new.to_value(apu.m), np.angle(H[:,:,1]))
axes[1,2].pcolormesh(xv_new.to_value(apu.m), yv_new.to_value(apu.m), np.angle(H[:,:,2]))

axes[0,0].set_title("$H_x$")
axes[0,1].set_title("$H_y$")
axes[0,2].set_title("$H_z$")

fig.suptitle("Plane at z={:.2f}$\lambda$".format(scatter_dist/wavel.to_value(apu.m)))


##now Im going to compute the FFT to get the far field result
fig, axes = plt.subplots(2,3)
for i in range(3):
    F_shift = np.fft.ifftshift(E[:,:,i])
    aux = np.fft.ifft2(F_shift)
    aux_shift = np.fft.fftshift(aux)
    axes[0,i].pcolormesh(xv_new.to_value(apu.m), yv_new.to_value(apu.m), np.abs(aux_shift))
    axes[1,i].pcolormesh(xv_new.to_value(apu.m), yv_new.to_value(apu.m), np.angle(aux_shift))
axes[0,0].set_title("$E_x$")
axes[0,1].set_title("$E_y$")
axes[0,2].set_title("$E_z$")
fig.suptitle("FFT of the nearfield E")


fig, axes = plt.subplots(2,3)
for i in range(3):
    F_shift = np.fft.ifftshift(H[:,:,i])
    aux = np.fft.ifft2(F_shift)
    aux_shift = np.fft.fftshift(aux)
    axes[0,i].pcolormesh(xv_new.to_value(apu.m), yv_new.to_value(apu.m), np.abs(aux_shift))
    axes[1,i].pcolormesh(xv_new.to_value(apu.m), yv_new.to_value(apu.m), np.angle(aux_shift))
axes[0,0].set_title("$H_x$")
axes[0,1].set_title("$H_y$")
axes[0,2].set_title("$H_z$")
fig.suptitle("FFT of the nearfield H")

"""



"""
curr = Je.value#.reshape((sampling,sampling,3))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_trisurf(xv_p.to_value(apu.m), yv_p.to_value(apu.m), zv_p.to_value(apu.m))
surf.set_facecolor(plt.cm.viridis(np.abs(curr[:,0])/np.max(np.abs(curr[:,0]))))

#ax.plot_surface(xv_p.to_value(apu.m), yv_p.to_value(apu.m), zv_p.to_value(apu.m), facecolors=plt.cm.viridis(np.abs(curr[:,:,0])/np.max(np.abs(curr[:,:,0]))))

#ax.plot_surface(xv_p.to_value(apu.m), yv_p.to_value(apu.m), zv_p.to_value(apu.m), facecolors=plt.cm.viridis(np.abs(curr[:,:,0])/np.max(np.abs(curr[:,:,0]))))
fig.suptitle("Induced currents on the surface\n\
piston: {:.3f}; x tilt: {:.3f}; y tilt:{:.3f}\n\
deform (x^2+y^2): {:.3f}; deform (x^2-y^2): {:.3f}".format(*params))
"""


plt.show()



