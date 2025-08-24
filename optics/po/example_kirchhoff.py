from kirchhoff_fresnel import *
from geometry import *
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
plane_width = wavel*10#1*apu.m
plane_height = wavel*1000#2*wavel#2*apu.m
circle_radius = 0.5*apu.m
plane_points = 128

#target points where to compute the E_r, H_r. Just took a plane at a given z
reflect_width = 8*apu.m
reflect_height = 1*wavel #plane_height-1*wavel
reflect_points = 128

##threads
max_threads = 8
batch_size = 256


####
x = np.linspace(-plane_width/2, plane_width/2, plane_points)
xv, yv = np.meshgrid(x,x)

plane_params = np.zeros(5)
plane_params[0] = plane_height.to_value(apu.m)
plane_params[1:] = np.random.random(4)

plane_pos, n, ds = deformed_circular_reflector(xv, yv, circle_radius, plane_params)


## incident field
E_i = np.ones(plane_pos.shape[0], dtype=complex)*apu.V/apu.m   ##its scalar

###
xs= np.linspace(-reflect_width/2, reflect_width/2, reflect_points)
xv_s, yv_s = np.meshgrid(xs,xs)
scatter_pos = apu.Quantity((xv_s.flatten(), yv_s.flatten(), reflect_height*np.ones(reflect_points**2))).T

##propagate

start = time.time()
E_r0 = kirchhoff_propagation(plane_pos, -n, ds, E_i, scatter_pos, wavel)
print("integration took %.4f"%(time.time()-start))

##vectorized
start = time.time()
E_r1 = kirchhoff_propagation_vector(plane_pos, -n, ds, E_i, scatter_pos, wavel)
print("vector integration took %.4f"%(time.time()-start))

start = time.time()
E_r2 = kirchhoff_propagation_batch(plane_pos, -n, ds, E_i, scatter_pos, wavel, max_threads=max_threads,
                                   batch_size=batch_size, vector_worker=0)
print("batch integration took %.4f"%(time.time()-start))

start = time.time()
E_r3 = kirchhoff_propagation_batch(plane_pos, -n, ds, E_i, scatter_pos, wavel, max_threads=max_threads,
                                   batch_size=batch_size, vector_worker=1)
print("batch vector integration took %.4f"%(time.time()-start))

E_r = E_r1




##make some plots
E = E_r.reshape((reflect_points, reflect_points))

fig, axes = plt.subplots(2,2)
axes[0,0].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.abs(E))
axes[1,0].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.angle(E))

F_shift = np.fft.ifftshift(E)
aux = np.fft.ifft2(F_shift)
aux_shift = np.fft.fftshift(aux)
axes[0,1].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.abs(aux_shift))
axes[1,1].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.angle(aux_shift))

axes[0,0].set_title('asb(E)')
axes[1,0].set_title('angle E')

axes[0,1].set_title('asb(FFT(E))')
axes[1,1].set_title('angle FFT(E)')


plt.show()





