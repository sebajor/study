from geometry import *



d1 = 12*apu.m
d2 = 0.75*apu.m
f1 = 4.8*apu.m
f_d = 8
s = 1.05        ##oversize of the secondary

r_min = 0.0001*apu.m
r_points = 128
t_points = 128


###
###
###

##get geometry
pr = np.linspace(r_min, d1/2, r_points)
sr = np.linspace(r_min, d2/2, r_points)
tetha = np.linspace(0, 2*np.pi, t_points)

pr_v, pt_v = np.meshgrid(pr, tetha)
sr_v, st_v = np.meshgrid(sr, tetha)


(p_pos, p_n, p_ds), (s_pos, s_n, s_ds), B = cassegrain_cylindrical(pr_v, pt_v, sr_v, 
                                                              st_v, f1, f_d, s=s)




###cassegrain plot

prim = p_pos.reshape((r_points, t_points, 3))
sec = s_pos.reshape((r_points, t_points, 3))


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(prim[:,:,0].to_value(apu.m), prim[:,:,1].to_value(apu.m),
                prim[:,:,2].to_value(apu.m))

ax.plot_surface(sec[:,:,0].to_value(apu.m), sec[:,:,1].to_value(apu.m),
                sec[:,:,2].to_value(apu.m))

plt.show()


