from geometry import *
from physical_optics import *
from kirchhoff_fresnel import *
from sources import *
import time
import numpy as np

###
### hyperparameters
###

freq = 92.4*apu.GHz
wavel = cte.c/freq

###cassegrain geometry
d1 = 12*apu.m
d2 = 0.75*apu.m
f1 = 4.8*apu.m
f_d = 8
s = 1.05        ##oversize of the secondary

r_min = 0.001*apu.m
r_points = 256
t_points = 512#256

##gaussian beam
edge_tapper = -5*apu.dB
horn_aperture = 5*apu.cm
k_hat = np.array((0,0,1))

##secondary offsets
sec_offsets = [0*apu.mm, 0*apu.mm, +15*apu.mm]


##aperture position
##for apex tx is at 1835 and the big maps are 3deg-->96mts (?)
aperture_height = 1835*apu.m#wavel*2101#10*apu.m
#aperture_width = wavel*3000 
aperture_width = 96*apu.m
##for spherical cut
aperture_deg = 3*apu.deg
aperture_points = 256

##
max_threads = 20
batch_size = 256

po = True
###
###
###

##get geometry
pr = np.linspace(r_min, d1/2, r_points)
sr = np.linspace(r_min, d2/2, r_points)
tetha = np.linspace(0, 2*np.pi, t_points, endpoint=False)

##add a shift on tetha to have triangles..
dt = (tetha[1]-tetha[0])/2

pr_v, pt_v = np.meshgrid(pr, tetha)
sr_v, st_v = np.meshgrid(sr, tetha)

##add a little noise to the values
#pr += np.random.randn(r_points)*1e-3*apu.m
#sr += np.random.randn(r_points)*1e-5*apu.m
#tetha += np.random.randn(t_points)*1e-5

#pt_v[:,::2] += dt/2
#st_v[:,::2] +=dt/2


(p_pos, p_n, p_ds), (s_pos, s_n, s_ds), B, s_focus = cassegrain_cylindrical(pr_v, pt_v, sr_v, 
                                                              st_v, f1, f_d, s=s)


s_pos[:,0] += sec_offsets[0]
s_pos[:,1] += sec_offsets[1]
s_pos[:,2] += sec_offsets[2]


##create source
source_x0 = np.array((0,0,B.to_value(apu.m))).T*apu.m
source = cylindrical_gaussian_beam(edge_tapper, horn_aperture, 
                                    wavel, source_x0, k_hat)
#source = plane_wave_source(freq=freq, x0=source_x0, k_hat=k_hat, E0=E0)
#E_i, H_i = source.propagate(s_pos)
E_i_kf = source.propagate(s_pos)
##manually do the vector 
eta = np.sqrt(cte.mu0/cte.eps0)
E_i = apu.Quantity((E_i_kf, np.zeros(E_i_kf.shape)*apu.V/apu.m,np.zeros(E_i_kf.shape)*apu.V/apu.m)).T
H_i = np.cross(k_hat[None, :], E_i)/eta

#E_i_kf = E_i[:,(E0.value).astype(bool)].flatten()   ##only valid when linearly polarized

#aperture plane
xs= np.linspace(-aperture_width/2, aperture_width/2, aperture_points)
xv_s, yv_s = np.meshgrid(xs,xs)
aperture_pos = apu.Quantity((xv_s.flatten(), yv_s.flatten(), aperture_height*np.ones(aperture_points**2))).T

#instead of aperture plane use a spherical cut
#at = np.linspace(-aperture_deg.to_value(apu.rad)/2, aperture_deg.to_value(apu.rad)/2, aperture_points)
#ap = np.linspace(0, 2*np.pi, aperture_points, endpoint=False)
#tt, pt = np.meshgrid(at, ap)
#z_s = np.cos(tt)*aperture_height
#x_s = np.sin(tt)*np.cos(pt)*aperture_height
#y_s = np.sin(tt)*np.sin(pt)*aperture_height

#aperture_pos = apu.Quantity((x_s.flatten(), y_s.flatten(), z_s.flatten())).T



##first reflection over the secondary
if(po):
    start = time.time()
    Je_s = compute_induced_currents(s_n, H_i)
    E_s_po, H_s_po = compute_reflected_fields_batch(s_pos, s_ds, Je_s, p_pos, wavel, 
                                                batch_size=batch_size, max_threads=max_threads)
    print("secondary integration done")
    Je_p = compute_induced_currents(p_n, H_s_po)
    E_p_po, H_p_po = compute_reflected_fields_batch(p_pos, p_ds, Je_p, aperture_pos, wavel, 
                                                batch_size=batch_size, max_threads=max_threads)

    print("PO integration took %.4f"%(time.time()-start))
start = time.time()
k_hat = np.zeros(3)
E_s_kf = kirchhoff_propagation_batch(s_pos, s_n, s_ds, E_i_kf, k_hat.T,
                                    p_pos, wavel, 
                                    max_threads=max_threads, batch_size=batch_size)
##Ill cheat a bit here..
k_r = np.zeros(3).T
##Ill compute the unit vectors that points from the imaginary focus of the secondary
#k_r = p_pos-apu.Quantity((0*apu.m, 0*apu.m, s_focus)).T
#k_r = k_r/np.sqrt(np.sum(k_r**2, axis=1))[:,None]

E_p_k = kirchhoff_propagation_batch(p_pos, s_n, s_ds, E_s_kf, k_r,
                                    aperture_pos, wavel,
                                    max_threads=max_threads, batch_size=batch_size)

print("KF integration took %.4f"%(time.time()-start))


"""

###cassegrain geometry plot
prim = p_pos.reshape((r_points, t_points, 3))
sec = s_pos.reshape((r_points, t_points, 3))


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(prim[:,:,0].to_value(apu.m), prim[:,:,1].to_value(apu.m),
                prim[:,:,2].to_value(apu.m))

ax.plot_surface(sec[:,:,0].to_value(apu.m), sec[:,:,1].to_value(apu.m),
                sec[:,:,2].to_value(apu.m))

plt.show()
"""


### beams plots
E_p_k = E_p_k.reshape((aperture_points, aperture_points))

pow_kf_db = 20*np.log10(np.abs(E_p_k.to_value(apu.V/apu.m)))
phase_kf = np.rad2deg(np.angle(E_p_k.to_value(apu.V/apu.m)))
if(po):
    E_p_po = E_p_po.reshape((aperture_points, aperture_points, 3))
    pow_po_db = 20*np.log10(np.abs(E_p_po.to_value(apu.V/apu.m)))
    phase_po = np.rad2deg(np.angle(E_p_po.to_value(apu.V/apu.m)))



fig, axes = plt.subplots(5,2)


axes[0,0].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.abs(E_p_po[:,:,0].to_value(apu.V/apu.m)))
axes[0,1].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.angle(E_p_po[:,:,0].to_value(apu.V/apu.m)))

axes[1,0].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.abs(E_p_po[:,:,1].to_value(apu.V/apu.m)))
axes[1,1].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.angle(E_p_po[:,:,1].to_value(apu.V/apu.m)))

axes[2,0].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.abs(E_p_k.to_value(apu.V/apu.m)))
axes[2,1].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.angle(E_p_k.to_value(apu.V/apu.m)))

axes[3,0].plot(xv_s[0,:].to_value(apu.m), 20*np.log10(np.abs(E_p_po[aperture_points//2,:,0].to_value(apu.V/apu.m))), label='PO x-pol')
axes[3,0].plot(xv_s[0,:].to_value(apu.m), 20*np.log10(np.abs(E_p_po[aperture_points//2,:,1].to_value(apu.V/apu.m))), label='PO y-pol')
axes[3,0].plot(xv_s[0,:].to_value(apu.m), 20*np.log10(np.abs(E_p_k[aperture_points//2,:].to_value(apu.V/apu.m))), label='KF')

axes[3,1].plot(xv_s[0,:].to_value(apu.m), np.angle(E_p_po[aperture_points//2,:,0].to_value(apu.V/apu.m)), label='PO x-pol')
axes[3,1].plot(xv_s[0,:].to_value(apu.m), np.angle(E_p_po[aperture_points//2,:,1].to_value(apu.V/apu.m)), label='PO y-pol')
axes[3,1].plot(xv_s[0,:].to_value(apu.m), np.angle(E_p_k[aperture_points//2,:].to_value(apu.V/apu.m)), label='KF')


axes[4,0].plot(xv_s[0,:].to_value(apu.m), 20*np.log10(np.abs(E_p_po[:, aperture_points//2,0].to_value(apu.V/apu.m))), label='PO x-pol')
axes[4,0].plot(xv_s[0,:].to_value(apu.m), 20*np.log10(np.abs(E_p_po[:,aperture_points//2,1].to_value(apu.V/apu.m))), label='PO y-pol')
axes[4,0].plot(xv_s[0,:].to_value(apu.m), 20*np.log10(np.abs(E_p_k[:,aperture_points//2].to_value(apu.V/apu.m))), label='KF')


axes[4,1].plot(xv_s[0,:].to_value(apu.m), np.angle(E_p_po[:, aperture_points//2,0].to_value(apu.V/apu.m)), label='PO x-pol')
axes[4,1].plot(xv_s[0,:].to_value(apu.m), np.angle(E_p_po[:,aperture_points//2,1].to_value(apu.V/apu.m)), label='PO y-pol')
axes[4,1].plot(xv_s[0,:].to_value(apu.m), np.angle(E_p_k[:,aperture_points//2].to_value(apu.V/apu.m)), label='KF')

axes[3,0].grid(); axes[3,1].grid(); axes[4,0].grid(); axes[4,1].grid()
axes[3,0].legend(); axes[3,1].legend(); axes[4,0].legend(); axes[4,1].legend()

plt.show()



