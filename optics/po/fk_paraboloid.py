from kirchhoff_fresnel import *
from physical_optics import *
from geometry import *
from sources import *
import time
import astropy

###
### hyperparameters
###
freq = 100*apu.GHz#100*apu.GHz
wavel = cte.c/freq

#PEC surface parameters
r_min = 0.01*apu.m
radius_points = 128
theta_points = 128
diameter = 12*apu.m
focus = 4.8*apu.m#8*diameter


##for the primary at apex we have D=12m, primary focal length=4.8m
## f/D = 8, secondary diameter=0.75m

##source parameters
source_x0 = np.array([0,0,100]).T*apu.m
k_hat = np.array((0,0,-1)).T
E0 = np.array((0,1,0)).T*apu.V/apu.m



#target points where to compute the E_r, H_r. Just took a plane at a given z
reflect_height = wavel*2#5000#6*apu.m#1*wavel #plane_height-1*wavel
reflect_width = wavel*8#0.5*apu.m#8*apu.m
reflect_points = 128

##farfield distance
#reflect_height = (2*diameter**2/wavel)/5

#
max_threads = 8
batch_size = 256

###
###

r = np.linspace(r_min, diameter/2, radius_points)
theta = np.linspace(0.001, 2*np.pi, theta_points, endpoint=False)
rv, tv = np.meshgrid(r, theta)

surf_points, n, ds = paraboloid_cylindrical(rv, tv, focus, diameter)


##this are the 3D fields, and the default is having E on x
source = plane_wave_source(freq=freq, x0=source_x0, k_hat=k_hat, E0=E0)
E_i, H_i = source.propagate(surf_points)
E_i_kf = E_i[:,(E0.value).astype(bool)].flatten()


##now we generate the plane where we want to compute the fields
xs= np.linspace(-reflect_width/2, reflect_width/2, reflect_points)
xv_s, yv_s = np.meshgrid(xs,xs)
scatter_pos = apu.Quantity((xv_s.flatten(), yv_s.flatten(), reflect_height*np.ones(reflect_points**2))).T



start = time.time()
E_r_v = kirchhoff_propagation_vector(surf_points, n, ds, E_i_kf, scatter_pos, wavel)
#E_r = kirchhoff_propagation(surf_points, n, ds, E_i, scatter_pos, wavel)
print("vector integration took %.4f"%(time.time()-start))


start = time.time()
Je = compute_induced_currents(n, H_i)      ##use -n since we are pointing down
E_r, H_r = compute_reflected_fields_batch(surf_points, ds, Je, scatter_pos, wavel, 
                                            batch_size=batch_size, max_threads=max_threads)
E_r_po= E_r*apu.V/apu.m
H_r_po = H_r*apu.A/apu.m
print("PO parallel integration took %.4f"%(time.time()-start))


##make resulting plot
E = E_r_po.reshape((reflect_points, reflect_points, 3))[:,:,0]
E_po = E_r_po.reshape((reflect_points, reflect_points, 3))
E_kf = E_r_v.reshape((reflect_points, reflect_points))


fig, axes = plt.subplots(2,2)
axes[0,0].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.abs(E))
axes[1,0].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.angle(E))

#far field transformation
F_shift = np.fft.ifftshift(E)
aux = np.fft.ifft2(F_shift)
E_ff= np.fft.fftshift(aux)

dx = xv_s[0,1]-xv_s[0,0]
dy = yv_s[1,0]-yv_s[0,0]

u,v = np.fft.fftfreq(xv_s.shape[0], dx), np.fft.fftfreq(yv_s.shape[1], dy)
if type(xv_s) == apu.quantity.Quantity:
    if astropy.__version__ < '4':
        u_shift = np.fft.fftshift(u) * xv_s.unit * wavel * apu.rad
        v_shift = np.fft.fftshift(v) * yv_s.unit * wavel * apu.rad
    else:
        u_shift = np.fft.fftshift(u) * wavel * apu.rad
        v_shift = np.fft.fftshift(v) * wavel * apu.rad
else:
    u_shift = np.fft.fftshift(u) * wavel.to_value(apu.m)
    v_shift = np.fft.fftshift(v) * wavel.to_value(apu.m)

uv, vv = np.meshgrid(u_shift, v_shift)


axes[0,1].pcolormesh(uv.to_value(apu.deg), vv.to_value(apu.deg), np.abs(E_ff))
axes[1,1].pcolormesh(uv.to_value(apu.deg), vv.to_value(apu.deg), np.angle(E_ff))

axes[0,0].set_title('asb(E)')
axes[1,0].set_title('angle E')

axes[0,1].set_title('asb(FFT(E))')
axes[1,1].set_title('angle FFT(E)')


fig, ax = plt.subplots(2,1)

##depending on the wavelenght the FFT could gives the far field or the aperture...

ff_x = 20*np.log10(np.abs(E_ff[:,reflect_points//2].value))
ff_y = 20*np.log10(np.abs(E_ff[reflect_points//2,:].value))
ff_max= np.max(np.array([ff_x, ff_y]))
ff_x -= ff_max
ff_y -= ff_max
ax[1].plot(uv[0,:].to_value(apu.deg), ff_x, color='darkblue', label='x cut')
ax[1].plot(uv[0,:].to_value(apu.deg), ff_y, color='darkred', label='y cut')

ax[1].axhline(-3, ls='--', color='black')
ax[1].set_ylim(-80,0)
ax[1].grid()
ax[1].legend()
ax[1].set_xlabel('deg')
ax[1].set_ylabel('dB')
ax[1].set_title("FFT(E) cut")




near_x = 20*np.log10(np.abs(E[:,reflect_points//2].value))
near_y = 20*np.log10(np.abs(E[reflect_points//2,:].value))
near_max= np.max(np.array([near_x, near_y]))
near_x -= near_max
near_y -= near_max

theta_x = np.arctan2(xv_s[0,:], reflect_height)


ax[0].plot(theta_x.to_value(apu.deg), near_x, color='darkblue', label='x cut')
ax[0].plot(theta_x.to_value(apu.deg), near_y, color='darkred', label='y cut')

ax[0].axhline(-3, ls='--', color='black')
ax[0].set_ylim(-80,0)
ax[0].grid()
ax[0].legend()
ax[0].set_xlabel('deg (trigonometry)')
ax[0].set_ylabel('dB')
ax[0].set_title("E cut")




##get the approximated HPBW
#ind_x = ff_x>-3
#ind_y = ff_y>-3 

#hpbw_x = uv[0,ind_x][-1] - uv[0,ind_x][0]
#hpbw_y = vv[ind_y,0][-1] - vv[ind_y,0][0]

gold_value_page = (7.8*apu.arcsec*(800/freq.to_value(apu.GHz)))
print("HPBW webpage: {:.4f} deg".format(gold_value_page.to_value(apu.deg)))

print("HPBW (70lambda/D): {:.4f} deg".format((70*wavel/diameter).decompose()))

"""
fig.suptitle("$HPBW_x$ = {:.4f} deg\t $HPBW_y$ = {:.4f} deg\nPage value: {:.4f} deg".format(
    hpbw_x.to_value(apu.deg),
    hpbw_y.to_value(apu.deg),
    gold_value_page.to_value(apu.deg))
             )
"""
plt.show()




###make  a plot
xv = surf_points[:,0].reshape((radius_points, theta_points))
yv = surf_points[:,1].reshape((radius_points, theta_points))
zv = surf_points[:,2].reshape((radius_points, theta_points))

nx = n[:,0].reshape((radius_points, theta_points))
ny = n[:,1].reshape((radius_points, theta_points))
nz = n[:,2].reshape((radius_points, theta_points))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(xv.to_value(apu.m), yv.to_value(apu.m), zv.to_value(apu.m))

ax.quiver(xv[::16,::16].to_value(apu.m), yv[::16,::16].to_value(apu.m), zv[::16,::16].to_value(apu.m), 
          nx[::16,::16], ny[::16,::16], nz[::16,::16],
          color='r', normalize=1)#, length=1.2)

plt.show()





"""
These are the cartesian way.. but the parametrization is not ok...
x = np.linspace(-plane_width/2, plane_width/2, plane_points)
xv, yv = np.meshgrid(x,x)

surf_pos, n, ds, mask = paraboloid_cartesian(xv, yv, focus, diameter)



###
###plot the paraboloid
###
z_plot = surf_pos[:,2].reshape((plane_points, plane_points))
n_plot = -n.reshape((plane_points, plane_points, 3))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

z_plot[~mask] = np.nan
#n = -n.reshape((plane_points, plane_points, 3))
ax.plot_surface(xv.to_value(apu.m), yv.to_value(apu.m), z_plot.to_value(apu.m))

ax.quiver(xv[::16,::16].to_value(apu.m), yv[::16,::16].to_value(apu.m), z_plot[::16,::16].to_value(apu.m), 
          n_plot[::16,::16,0], n_plot[::16,::16,1], n_plot[::16,::16,2],
          color='r', normalize=1)

#ax.plot_trisurf(xv[mask].to_value(apu.m), yv[mask].to_value(apu.m), surf_pos[mask].to_value(apu.m))
plt.show()
"""
