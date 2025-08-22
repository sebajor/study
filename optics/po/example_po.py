from physical_optics import *
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
plane_width = 1*apu.m
plane_height = 2*wavel#2*apu.m
circle_radius = 0.5*apu.m
plane_points = 128

#target points where to compute the E_r, H_r. Just took a plane at a given z
reflect_width = 8*apu.m
reflect_height = 1*wavel #plane_height-1*wavel
reflect_points = 128

#
max_threads = 8
batch_size = 256



###
###
x = np.linspace(-plane_width/2, plane_width/2, plane_points)
xv, yv = np.meshgrid(x,x)

plane_params = np.zeros(5)
plane_params[0] = plane_height.to_value(apu.m)

plane_pos, n, ds = deformed_circular_reflector(xv, yv, circle_radius, plane_params)

###
### PO is time independent, then the plane wave at a given z is a constant
### Ill took E = Ex and H = Hy and k=kz
###
eta0 = np.sqrt(cte.mu0/cte.eps0)
H_i = np.zeros(plane_pos.shape, dtype=complex)*apu.A/apu.m
H_i[:,1] = 1*apu.V/apu.m/eta0

###
xs= np.linspace(-reflect_width/2, reflect_width/2, reflect_points)
xv_s, yv_s = np.meshgrid(xs,xs)
scatter_pos = apu.Quantity((xv_s.flatten(), yv_s.flatten(), reflect_height*np.ones(reflect_points**2))).T

###
###Ok, now we should have everything that we need
start = time.time()

Je = compute_induced_currents(-n, H_i)      ##use -n since we are pointing down
#E_r, H_r = compute_reflected_fields(plane_pos, ds, Je, scatter_pos, wavel)

print("integration took %.4f"%(time.time()-start))

start = time.time()
E_r, H_r = compute_reflected_fields_batch(plane_pos, ds, Je, scatter_pos, wavel, 
                                            batch_size=batch_size, max_threads=max_threads)
print("parallel integration took %.4f"%(time.time()-start))




###Now Ill do some plots

E = E_r.reshape((reflect_points,reflect_points,3))
H = H_r.reshape((reflect_points,reflect_points,3))


##some plots
fig, axes = plt.subplots(2,3)
axes[0,0].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.abs(E[:,:,0]))
axes[0,1].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.abs(E[:,:,1]))
axes[0,2].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.abs(E[:,:,2]))

axes[1,0].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.angle(E[:,:,0]))
axes[1,1].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.angle(E[:,:,1]))
axes[1,2].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.angle(E[:,:,2]))

axes[0,0].set_title("$E_x$")
axes[0,1].set_title("$E_y$")
axes[0,2].set_title("$E_z$")

fig.suptitle("Plane at z={:.2f}$\lambda$".format(reflect_height/wavel))


fig, axes = plt.subplots(2,3)
axes[0,0].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.abs(H[:,:,0]))
axes[0,1].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.abs(H[:,:,1]))
axes[0,2].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.abs(H[:,:,2]))

axes[1,0].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.angle(H[:,:,0]))
axes[1,1].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.angle(H[:,:,1]))
axes[1,2].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.angle(H[:,:,2]))

axes[0,0].set_title("$H_x$")
axes[0,1].set_title("$H_y$")
axes[0,2].set_title("$H_z$")

fig.suptitle("Plane at z={:.2f}$\lambda$".format(reflect_height/wavel))


##now Im going to compute the FFT to get the far field result
fig, axes = plt.subplots(2,3)
for i in range(3):
    F_shift = np.fft.ifftshift(E[:,:,i])
    aux = np.fft.ifft2(F_shift)
    aux_shift = np.fft.fftshift(aux)
    axes[0,i].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.abs(aux_shift))
    axes[1,i].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.angle(aux_shift))
axes[0,0].set_title("$E_x$")
axes[0,1].set_title("$E_y$")
axes[0,2].set_title("$E_z$")
fig.suptitle("FFT of the nearfield E")


fig, axes = plt.subplots(2,3)
for i in range(3):
    F_shift = np.fft.ifftshift(H[:,:,i])
    aux = np.fft.ifft2(F_shift)
    aux_shift = np.fft.fftshift(aux)
    axes[0,i].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.abs(aux_shift))
    axes[1,i].pcolormesh(xv_s.to_value(apu.m), yv_s.to_value(apu.m), np.angle(aux_shift))
axes[0,0].set_title("$H_x$")
axes[0,1].set_title("$H_y$")
axes[0,2].set_title("$H_z$")
fig.suptitle("FFT of the nearfield H")


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




