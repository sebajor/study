import numpy as np
import matplotlib.pyplot as plt
from sources import cylindrical_gaussian_beam
from astropy import units as apu
from astropy import constants as cte


###
### hypoerparameters
###

freq = 100*apu.GHz
edge_tapper = -20*apu.dB
horn_aperture = 5*apu.cm

source_x0 = np.array([0,0,0])*apu.m
propagation = np.array([0,0,1])

x_val= 0.25* apu.m
#z_val = [0.01*apu.m, 10*apu.m]

x_points = 64
z_points = 32


###
###
###

wavel  = cte.c/freq


source = cylindrical_gaussian_beam(edge_tapper, horn_aperture, 
                                    wavel, source_x0, propagation)

z_val =  [source.z_c*0.1, source.z_c*5]

x = np.linspace(-x_val/2, x_val/2, x_points)
z = np.linspace(z_val[0], z_val[1], z_points)
xv, yv,zv = np.meshgrid(x,x,z)
test_points = apu.Quantity((xv.flatten(), yv.flatten(), zv.flatten())).T


out = source.propagate(test_points)


out = out.reshape((x_points, x_points, z_points))

##make some plots
ind = np.random.randint(low=0, high=z_points,size=5)
ind = np.sort(np.unique(ind))

fig, axes = plt.subplots(len(ind),2)

for i in range(len(ind)):
    axes[i,0].pcolormesh(xv[:,:,0].to_value(apu.m), yv[:,:,0].to_value(apu.m), np.abs(out[:,:,ind[i]].to_value(apu.V/apu.m)))
    axes[i,1].pcolormesh(xv[:,:,0].to_value(apu.m), yv[:,:,0].to_value(apu.m), np.angle(out[:,:,ind[i]].to_value(apu.V/apu.m)))
    axes[i,0].set_title("z: {:.3f}\t z/z_c: {:.3f}".format(z[ind[i]].to_value(apu.m),z[ind[i]]/source.z_c))

plt.show()



