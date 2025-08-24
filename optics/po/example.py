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
circle_radius = 0.5*apu.m
plane_points = 128

#target points where to compute the E_r, H_r. Just took a plane at a given z
reflect_width = 100*wavel#8*apu.m
reflect_height = 2000*wavel #plane_height-1*wavel
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
#plane_params[1:] = np.random.random(4)

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
E_r_k = kirchhoff_propagation_vector(plane_pos, -n, ds, E_i_kf, scatter_pos, wavel)
print("vector integration took %.4f"%(time.time()-start))


E_po = E_r_po.reshape((reflect_points, reflect_points,3))*apu.V/apu.m
E_kf = E_r_k.reshape((reflect_points, reflect_points))


