import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chisquare


###
### Codes from https://github.com/jeffmcm1977/ASTR30600/blob/main/Notebook2_Statistics.ipynb
###

##correlation function for galaxy-galaxy
#C(r) = A*(1/10)**(r/50)+B*np.exp((-1./2*(r-120)/10)**2)

##hyperparameters
A = 1.
B = 0.03
n_r = 200       #test point
n_data_pts = 20
pts_in_bin = 1000         ##number of samples per bin
bin_corr = 0.9          ##correlation between 2 neighbor bin points
A_search = [0.6,1.4,100] #fit search=init,end, points
B_search = [0.,0.04,100] #fit search=init,end, points


###
bin_width = n_r//n_data_pts
sigma_corr = 0.02*np.sqrt(pts_in_bin)

fig, axes = plt.subplots(1,2)

##create the theoric data
r = np.arange(n_r) + 10
gal_gal_cor_empricial_theory = A*(1/10.)**(r/50.)+ B*np.exp(-0.5*((r-120)/10.)**2)
axes[0].plot(r,gal_gal_cor_empricial_theory, label='Theory')
axes[0].set_xlabel("r (MPc / h)"); axes[0].set_ylabel("correlation function (arb)")

axes[1].plot(r,gal_gal_cor_empricial_theory, label='Theory')
axes[1].set_xlabel("r (MPc / h)"); axes[1].set_ylabel("correlation function (arb)")

#create uncorrelated data
sample_r = np.arange(len(r))[::bin_width]                                                   ##sampled r
noise = np.random.randn((pts_in_bin*len(sample_r))).reshape((len(sample_r), pts_in_bin))    ##create noise matrix   

theory_mean = np.repeat(gal_gal_cor_empricial_theory[sample_r], pts_in_bin).reshape(-1,pts_in_bin) 
bin_data = noise*sigma_corr+theory_mean
mean_pt = np.mean(bin_data, axis=1)
error_pt = np.std(bin_data, axis=1)/np.sqrt(pts_in_bin-1)
axes[0].errorbar(r[sample_r], mean_pt, error_pt, marker=',', mec='red', mfc='red', c='red')
axes[0].set_title('Uncorrelated noisee')


##now we are going to add a correlation between the sucessive samples
corr_noise = np.zeros(noise.shape)
corr_noise[1:-1,:] = noise[1:-1,:]+noise[:-2,:]*bin_corr+noise[2:,:]*bin_corr
corr_noise[0,:] = noise[0,:]+noise[1,:]*bin_corr
corr_noise[-1,:] = noise[-1,:]+noise[-2,:]*bin_corr
#normalize the noise
corr_noise = corr_noise/np.repeat(np.std(corr_noise, axis=1), pts_in_bin).reshape((-1,pts_in_bin))
bin_data_corr = corr_noise*sigma_corr+theory_mean
mean_pt_corr = np.mean(bin_data_corr, axis=1)
error_pt_corr = np.std(bin_data_corr, axis=1)/np.sqrt(pts_in_bin-1)

axes[1].errorbar(r[sample_r], mean_pt_corr, error_pt_corr, marker=',', mec='red', mfc='red', c='red')
axes[1].set_title('Correlated noise')

axes[0].grid()
axes[1].grid()

#####There is a problem with my chi square code!!!!

##lets fit the function to get A,B
def fit_function(A,B,r):
    out= A*(1/10.)**(r/50.)+ B*np.exp(-0.5*((r-120)/10.)**2)
    return out

def chi_squared(r,mean_data, invCov, A,B):
    """
    inv Cov: inverse of the correlation matrix
    """
    model = fit_function(A,B,r)
    err = mean_data-model
    chi_sq = np.dot(np.transpose(err), np.matmul(invCov, err))
    return chi_sq


##The Chi**2 = sum(y_i-f(x_i))**2/sigma_ij where the sigma_ij is the covariance matrix

##first we are going to make an exploration of the A,B space assuming non-corelated noise
##there is something tricky here!!! 
A_points = np.linspace(A_search[0], A_search[1], A_search[2])
B_points = np.linspace(B_search[0], B_search[1], B_search[2])
chi_sq_pts = np.zeros((len(A_points), len(B_points)))

invCov_nocorr = np.diag(error_pt**(-2))


for i in range(len(A_points)):
    for j in range(len(B_points)):
        chi_sq_pts[i,j] = chi_squared(sample_r, mean_pt, invCov_nocorr, A_points[i], B_points[j])

##plot of the search space

delta_chi = chi_sq_pts-np.min(chi_sq_pts)
plt.figure()
plt.contour(B_points,A_points,delta_chi,levels=np.array([1,2**2,3**2,4**2,5**2]))
plt.xlabel('B')
plt.ylabel('A')

ind = np.where(chi_sq_pts==np.min(chi_sq_pts))
print('Actual value A={:}, B={:}'.format(A,B))
print('Best fit A={:} B={:}'.format(A_points[ind[1]], B_points[ind[0]]))


###in theory we need to use the cov matrix..so
cov_mat = np.cov(bin_data_corr)
##to invert a matrix the determinant should be !=0 and follow the same procedure..



plt.show()     


