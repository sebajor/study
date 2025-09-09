from physical_optics import *
from kirchhoff_fresnel import *
from geometry import *
from sources import *
import time

###
### circular reflector, its a circular PEC that reflects a plane wave
###

###
### hyperparameters
###
freq = 100*apu.GHz
wavel = cte.c/freq

#PEC surface parameters
plane_width = 1*apu.m
plane_height = 2*wavel#2*apu.m
circle_radius =0.25*apu.m# 0.5*apu.m
plane_points = 128

#target points where to compute the E_r, H_r. Just took a plane at a given z
reflect_width = 100*wavel#8*apu.m
reflect_height = 2101*wavel #plane_height-1*wavel
reflect_points = 128

##source parameters
source_x0 = np.array([0,0,100]).T*apu.m
k_hat = np.array((0,0,1)).T
E0 = np.array((1,0,0)).T*apu.V/apu.m

#
max_threads = 8
batch_size = 256



###
###
x = np.linspace(-plane_width/2, plane_width/2, plane_points)
xv, yv = np.meshgrid(x,x)

plane_params = np.zeros(5)
plane_params[0] = plane_height.to_value(apu.m)
#plane_params[1:] = np.random.random(4)*5

plane_pos, n, ds = deformed_circular_reflector(xv, yv, circle_radius, plane_params)

##create source
source = plane_wave_source(freq=freq, x0=source_x0, k_hat=k_hat, E0=E0)
E_i, H_i = source.propagate(plane_pos)
E_i_kf = E_i[:,(E0.value).astype(bool)].flatten()



xs= np.linspace(-reflect_width/2, reflect_width/2, reflect_points)
xv_s, yv_s = np.meshgrid(xs,xs)
scatter_pos = apu.Quantity((xv_s.flatten(), yv_s.flatten(), reflect_height*np.ones(reflect_points**2))).T

start = time.time()
Je = compute_induced_currents(-n, H_i)      ##use -n since we are pointing down
E_r_po, H_r_po = compute_reflected_fields_batch(plane_pos, ds, Je, scatter_pos, wavel, 
                                            batch_size=batch_size, max_threads=max_threads)
print("parallel integration took %.4f"%(time.time()-start))


##vectorized
start = time.time()
E_r_k = kirchhoff_propagation_batch(plane_pos, -n, ds, E_i_kf, k_hat, scatter_pos, wavel,
                                    max_threads=max_threads, batch_size=batch_size)
print("vector integration took %.4f"%(time.time()-start))


E_po = E_r_po.reshape((reflect_points, reflect_points,3))
E_kf = E_r_k.reshape((reflect_points, reflect_points))


fig, axes = plt.subplots(3,2)

axes[0,0].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.abs(E_po[:,:,0].to_value(apu.V/apu.m)))
axes[0,1].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.angle(E_po[:,:,0].to_value(apu.V/apu.m)))
axes[1,0].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.abs(E_kf[:,:].to_value(apu.V/apu.m)))
axes[1,1].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.angle(E_kf[:,:].to_value(apu.V/apu.m)))

axes[2,0].plot(xv_s[0,:].to_value(apu.m), 20*np.log10(np.abs(E_po[reflect_points//2,:,0].to_value(apu.V/apu.m))), color='red', label='PO $E_{x}$')
axes[2,0].plot(xv_s[0,:].to_value(apu.m), 20*np.log10(np.abs(E_kf[reflect_points//2,:].to_value(apu.V/apu.m))), color='black', ls='--', label='KF $E}$')

axes[2,1].plot(xv_s[0,:].to_value(apu.m), np.rad2deg(np.angle(E_po[reflect_points//2,:,0].to_value(apu.V/apu.m))), color='red', label='PO $E_{x}$')
axes[2,1].plot(xv_s[0,:].to_value(apu.m), np.rad2deg(np.angle(E_kf[reflect_points//2,:].to_value(apu.V/apu.m))), color='black', ls='--', label='KF $E$')

axes[0,0].set_title("PO abs($E_x$)")
axes[0,1].set_title("PO angle($E_x$)")

axes[1,1].set_title("KF angle(E)")
axes[1,0].set_title("KF abs(E)")


axes[2,0].set_title("X cut abs")
axes[2,1].set_title("X cut angle")
axes[2,0].set_ylabel('dB')
axes[2,1].set_ylabel('deg')
axes[2,0].grid()
axes[2,1].grid()
axes[2,0].legend()
axes[2,1].legend()



plt.show()




