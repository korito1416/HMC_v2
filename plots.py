#!/usr/bin/env python

# Import Required Packages
# ========================
import os, sys
import pickle
import time
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(font_scale=1.2)
# Import the solvers
import solvers
from scipy.stats import truncnorm
sys.path.append(os.path.abspath("src"))
from data_handlers import load_site_data
from scipy.integrate import quad


########################################################################
import argparse
parser = argparse.ArgumentParser(description="parameter settings")
parser.add_argument("--weight",type=float,default=0.25)
parser.add_argument("--xi",type=float,default=0.01)
parser.add_argument("--pf",type=float,default=20.76)
parser.add_argument("--pa",type=float,default=44.75)
parser.add_argument("--theta",type=float,default=1.0)
parser.add_argument("--gamma",type=float,default=1.0)
parser.add_argument("--sitenum",type=int,default=10)
parser.add_argument("--time",type=int,default=200)
parser.add_argument("--dataname",type=str,default="tests")
parser.add_argument("--mix_in",type=int,default=2)
parser.add_argument("--mass_matrix_theta_scale",type=float,default=1.0)
parser.add_argument("--mass_matrix_gamma_scale",type=float,default=1.0)
parser.add_argument("--mass_matrix_weight",type=float,default=0.1)
parser.add_argument("--symplectic_integrator_num_steps",type=int,default=2)
parser.add_argument("--stepsize",type=float,default=0.1)
parser.add_argument("--scale",type=float,default=1.0)
parser.add_argument("--mode",type=float,default=1.0)


args = parser.parse_args()
weight = args.weight
pf = args.pf
pa = args.pa
theta_multiplier = args.theta
gamma_multiplier = args.gamma
sitenum = args.sitenum
time = args.time
xi = args.xi
dataname = args.dataname
mix_in= args.mix_in
mass_matrix_theta_scale=args.mass_matrix_theta_scale
mass_matrix_gamma_scale=args.mass_matrix_gamma_scale
mass_matrix_weight=args.mass_matrix_weight
symplectic_integrator_num_steps=args.symplectic_integrator_num_steps
stepsize=args.stepsize
scale = args.scale
mode = args.mode

workdir = os.getcwd()
output_dir = workdir+"/output/"+dataname+"/scale_"+str(scale)+"_mode_"+str(mode)+"/pf_"+str(pf)+"_pa_"+str(pa)+"_time_"+str(time)+"/theta_"+str(theta_multiplier)+"_gamma_"+str(gamma_multiplier)+"/sitenum_"+str(sitenum)+"_xi_"+str(xi)+"/mix_in_"+str(mix_in)+"_mm_theta_scale_"+str(mass_matrix_theta_scale)+"_mm_gamma_scale_"+str(mass_matrix_gamma_scale)+"_num_steps_"+str(symplectic_integrator_num_steps)+"_stepsize_"+str(stepsize)+"/weight_"+str(weight)+"_mass_matrix_weight_"+str(mass_matrix_weight)+"/"
plotdir = workdir+"/plot/"+dataname+"/scale_"+str(scale)+"_mode_"+str(mode)+"/pf_"+str(pf)+"_pa_"+str(pa)+"_time_"+str(time)+"/theta_"+str(theta_multiplier)+"_gamma_"+str(gamma_multiplier)+"/sitenum_"+str(sitenum)+"_xi_"+str(xi)+"/mix_in_"+str(mix_in)+"_mm_theta_scale_"+str(mass_matrix_theta_scale)+"_mm_gamma_scale_"+str(mass_matrix_gamma_scale)+"_num_steps_"+str(symplectic_integrator_num_steps)+"_stepsize_"+str(stepsize)+"/weight_"+str(weight)+"_mass_matrix_weight_"+str(mass_matrix_weight)+"/"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
if not os.path.exists(plotdir):
    os.makedirs(plotdir)


(    zbar_2017,
    gamma,
    gammaSD,
    z_2017,
    forestArea_2017_ha,
    theta,
    thetaSD,
) = load_site_data(sitenum, norm_fac=1e9, )



with open(output_dir+'results.pcl', 'rb') as f:
    # Load the data from the file
    results = pickle.load(f)

fig, axes = plt.subplots(1, 1, figsize = (8,6))
plt.plot(results['abs_error_tracker'], label=r"Absolute Error")
plt.xlabel("Iteration")
plt.ylabel(r"Absolute Error")
plt.title(r"Trace Plot of Absolute Error")
legend = plt.legend(bbox_to_anchor=(1.05, 0.5), loc="center left", borderaxespad=0)
fig.tight_layout()
plt.subplots_adjust(right=0.7) 
fig.savefig(plotdir +'abs_error.png', bbox_extra_artists=(legend,), bbox_inches='tight', dpi = 100)
plt.close()

fig, axes = plt.subplots(1, 1, figsize = (8,6))
plt.plot(results['percentage_error_tracker'], label=r"Proportional Error")
plt.xlabel("Iteration")
plt.ylabel(r"Proportional Error")
plt.title(r"Trace Plot of Proportional Error")
legend = plt.legend(bbox_to_anchor=(1.05, 0.5), loc="center left", borderaxespad=0)
fig.tight_layout()
plt.subplots_adjust(right=0.7) 
fig.savefig(plotdir +'pro_error.png', bbox_extra_artists=(legend,), bbox_inches='tight', dpi = 100)
plt.close()


size = results['size']
diff = abs(np.diff(results['uncertain_vals_tracker'], axis=0)) / results['uncertain_vals_tracker'][:-1, :] 
fig, axes = plt.subplots(1, 2, figsize=(16,6))
for i in range(size):
    axes[0].plot(diff[:, i], label=f'Theta {i+1}')
axes[0].set_title('Theta Proportional Error')
for i in range(size, diff.shape[1]):
    axes[1].plot(diff[:, i], label=f'Gamma {i+1-size}')
axes[1].set_title('Gamma Proportional Error')
y_min = np.min(diff)
y_max = np.max(diff)
axes[0].set_ylim([y_min, y_max])
axes[1].set_ylim([y_min, y_max])
fig.tight_layout()
fig.savefig(plotdir +'site_pro_error.png', bbox_extra_artists=(legend,), bbox_inches='tight', dpi = 100)
plt.close()


fig, axes = plt.subplots(1, 1, figsize = (8,6))
for j in range(results['size'],results['size']*2):
    plt.plot(results['uncertain_vals_tracker'][:, j], label=r"$\gamma_{%d}$"%(j+1))
plt.xlabel("Iteration")
plt.ylabel(r"$\gamma$")
plt.title(r"Trace Plot of $\gamma$")
legend = plt.legend(bbox_to_anchor=(1.05, 0.5), loc="center left", borderaxespad=0)
fig.tight_layout()
plt.subplots_adjust(right=0.7) 
fig.savefig(plotdir +'gamma.png', bbox_extra_artists=(legend,), bbox_inches='tight', dpi = 100)
plt.close()

fig, axes = plt.subplots(1, 1, figsize = (8,6))
for j in range(results['size']):
    plt.plot(results['uncertain_vals_tracker'][:, j], label=r"$\theta_{%d}$"%(j+1))
plt.xlabel("Iteration")
plt.ylabel(r"$\theta$")
plt.title(r"Trace Plot of $\theta$")
legend = plt.legend(bbox_to_anchor=(1.05, 0.5), loc="center left", borderaxespad=0)
fig.tight_layout()
plt.subplots_adjust(right=0.7) 
fig.savefig(plotdir +'theta.png', bbox_extra_artists=(legend,), bbox_inches='tight', dpi = 100)
plt.close()

# fig, axes = plt.subplots(1, 1, figsize = (8,6))
# for j in range(results['size']+2):
#     plt.plot(results['sol_val_X_tracker'][:, j], label=r"$X_{%d}$"%(j+1))
# plt.xlabel("Iteration")
# plt.ylabel(r"$X$")
# plt.title(r"Trace Plot of X")
# legend = plt.legend(bbox_to_anchor=(1.05, 0.5), loc="center left", borderaxespad=0)
# fig.tight_layout()
# plt.subplots_adjust(right=0.7) 
# fig.savefig(plotdir +'X.png', bbox_extra_artists=(legend,), bbox_inches='tight', dpi = 100)
# plt.close()

# fig, axes = plt.subplots(1, 1, figsize = (8,6))
# for j in range(results['size']+2):
#     plt.plot(results['sol_val_Ua_tracker'][:, j], label=r"$Ua_{%d}$"%(j+1))
# plt.xlabel("Iteration")
# plt.ylabel(r"$Ua$")
# plt.title(r"Trace Plot of Ua")
# legend = plt.legend(bbox_to_anchor=(1.05, 0.5), loc="center left", borderaxespad=0)
# fig.tight_layout()
# plt.subplots_adjust(right=0.7)
# fig.savefig(plotdir +'Ua.png', bbox_extra_artists=(legend,), bbox_inches='tight', dpi = 100)
# plt.close()

# size = results['size']
# for j in range(size):
#     # for i in range(len(results['sol_val_Um_tracker'])):
#         i = len(results['sol_val_Up_tracker'])-1
#         fig, axes = plt.subplots(1, 1, figsize = (8,6))
#         plt.plot(results['sol_val_Um_tracker'][i][j,:], label=r"site_%d_iter_%d"%(j+1, i+1))
#         plt.xlabel("Iteration")
#         plt.ylabel(r"$Um$")
#         plt.title(r"Trace Plot of Um for site_%d_iter_%d"%(j+1, i+1))
#         legend = plt.legend(bbox_to_anchor=(1.05, 0.5), loc="center left", borderaxespad=0)
#         fig.tight_layout()
#         plt.subplots_adjust(right=0.7)
#         fig.savefig(plotdir +'Um_site_%d_iter_%d.png'%(j+1, i+1), bbox_extra_artists=(legend,), bbox_inches='tight', dpi = 100)
#         plt.close()

# # For Up
# for j in range(size):
#     # for i in range(len(results['sol_val_Up_tracker'])):
#         i = len(results['sol_val_Up_tracker'])-1
#         fig, axes = plt.subplots(1, 1, figsize = (8,6))
#         plt.plot(results['sol_val_Up_tracker'][i][j,:], label=r"$Up_{site_%d, iter_%d}$"%(j+1, i))
#         plt.xlabel("Iteration")
#         plt.ylabel(r"$Up$")
#         plt.title(r"Trace Plot of Up")
#         legend = plt.legend(bbox_to_anchor=(1.05, 0.5), loc="center left", borderaxespad=0)
#         fig.tight_layout()
#         plt.subplots_adjust(right=0.7)
#         fig.savefig(plotdir + 'Up_site_%d_iter_%d.png'%(j+1, i), bbox_extra_artists=(legend,), bbox_inches='tight', dpi = 100)
#         plt.close()

# # For Z
# for j in range(size):
#     # for i in range(len(results['sol_val_Z_tracker'])):
#         i = len(results['sol_val_Z_tracker'])-1
#         fig, axes = plt.subplots(1, 1, figsize = (8,6))
#         plt.plot(results['sol_val_Z_tracker'][i][j,:], label=r"$Z_{site_%d, iter_%d}$"%(j+1, i))
#         plt.xlabel("Iteration")
#         plt.ylabel(r"$Z$")
#         plt.title(r"Trace Plot of Z")
#         legend = plt.legend(bbox_to_anchor=(1.05, 0.5), loc="center left", borderaxespad=0)
#         fig.tight_layout()
#         plt.subplots_adjust(right=0.7)
#         fig.savefig(plotdir + 'Z_site_%d_iter_%d.png'%(j+1, i), bbox_extra_artists=(legend,), bbox_inches='tight', dpi = 100)
#         plt.close()


size = results['size']
np.random.seed(256)
for j in range(size):

    num_samples = len(results['collected_ensembles'][len(results['collected_ensembles'])-1][:, j])
    mu = theta[j]  # Assuming theta is your mean array
    sigma = thetaSD[j]  # Assuming thetaSD is your standard deviation array
    theta_samples = np.random.normal(mu, sigma, 50000)

    mu = gamma[j]  # Assuming gamma is your mean array
    sigma = gammaSD[j]  # Assuming gammaSD is your standard deviation array
    gamma_samples = np.random.normal(mu, sigma, 50000)
    
    # Find min and max across all iterations for the same site
    min_theta = np.min([np.min(results['collected_ensembles'][i][:, j]) for i in range(len(results['collected_ensembles']))]+ [np.min(theta_samples)])
    max_theta = np.max([np.max(results['collected_ensembles'][i][:, j]) for i in range(len(results['collected_ensembles']))]+ [np.max(theta_samples)])

    min_gamma = np.min([np.min(results['collected_ensembles'][i][:, j + size]) for i in range(len(results['collected_ensembles']))]+ [np.min(gamma_samples)])
    max_gamma = np.max([np.max(results['collected_ensembles'][i][:, j + size]) for i in range(len(results['collected_ensembles']))]+ [np.max(gamma_samples)])


    # for i in range(len(results['collected_ensembles'])):
    i = len(results['sol_val_Z_tracker'])-1
    i=26

    # i = 0
        # For theta parameters
    fig, ax1 = plt.subplots(1, 1, figsize = (8,6))
    sns.histplot(theta_samples[theta_samples>0], bins=100, label="Unadjusted", kde=False, color='blue', ax=ax1)
    ax1.set_ylabel('Count (Unadjusted)')
    ax2 = ax1.twinx()
    sns.histplot(results['collected_ensembles'][i][:, j][results['collected_ensembles'][i][:, j]>0], bins=100, label="Adjusted", kde=False, color='red', ax=ax2)
    ax2.set_ylabel('Count (Adjusted)')
    plt.xlim([min_theta, max_theta])  # Set x-axis limits
    plt.xlabel(r"$\theta_{site_%d}$"%(j+1))
    # plt.title(r"Distribution of $\theta_{site_%d}$ for iteration %d"%(j+1, i))
    if mode == 2.0:
        plt.title(r"Distribution of $\theta_{site_%d}$ truncated normal methods"%(j+1))
    else:
        plt.title(r"Distribution of $\theta_{site_%d}$ reflection boundary methods"%(j+1))
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc=0)
    ax1.grid(False)
    ax2.grid(False)
    fig.savefig(plotdir + 'theta_site_%d_iter_%d_hist.png'%(j+1, i), dpi = 100)
    plt.close()


    fig, ax1 = plt.subplots(1, 1, figsize = (8,6))
    sns.histplot(gamma_samples[gamma_samples>0], bins=100, label="Unadjusted", kde=False, color='blue', ax=ax1)
    ax1.set_ylabel('Count (Unadjusted)')
    ax2 = ax1.twinx()
    sns.histplot(results['collected_ensembles'][i][:, j+size][results['collected_ensembles'][i][:, j+size]>0], bins=100, label="Adjusted", kde=False, color='red', ax=ax2)
    ax2.set_ylabel('Count (Adjusted)')
    plt.xlim([min_gamma, max_gamma])  # Set x-axis limits
    plt.xlabel(r"$\gamma_{site_%d}$"%(j+1))
    if mode == 2.0:
        plt.title(r"Distribution of $\gamma_{site_%d}$ for truncated normal methods"%(j+1))
    else:
        plt.title(r"Distribution of $\gamma_{site_%d}$ for reflection boundary methods"%(j+1))
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc=0)
    ax1.grid(False)
    ax2.grid(False)
    fig.savefig(plotdir + 'gamma_site_%d_iter_%d_hist.png'%(j+1, i), dpi = 100)
    plt.close()

    if mode == 2.0:
        fig, axes = plt.subplots(1, 1, figsize = (8,6))
        # sns.kdeplot(theta_samples, label="Unadjusted", shade=True, clip=(0, None), color='blue')
        # sns.kdeplot(results['collected_ensembles'][i][:, j],  label="Adjusted", shade=True, clip=(0, None), color='red')
        a, b = (0 - np.mean(theta_samples)) / np.std(theta_samples), np.inf
        unadjusted_dist = truncnorm(a, b, loc=np.mean(theta_samples), scale=np.std(theta_samples))
        a, b = (0 - np.mean(results['collected_ensembles'][i][:, j])) / np.std(results['collected_ensembles'][i][:, j]), np.inf
        adjusted_dist = truncnorm(a, b, loc=np.mean(results['collected_ensembles'][i][:, j]), scale=np.std(results['collected_ensembles'][i][:, j]))
        x = np.linspace(min_theta, max_theta, 1000)
        axes.plot(x, unadjusted_dist.pdf(x), label="Unadjusted (truncnorm)", color='blue')  # plot scipy result as dashed
        axes.fill_between(x, unadjusted_dist.pdf(x), color='blue', alpha=0.3)  # Shaded area for unadjusted
        axes.plot(x, adjusted_dist.pdf(x), label="Adjusted (truncnorm)", color='red')  # plot scipy result as dashed
        axes.fill_between(x, adjusted_dist.pdf(x), color='red', alpha=0.3) 
        unadjusted_integral, _ = quad(unadjusted_dist.pdf, min_theta, max_theta)
        adjusted_integral, _ = quad(adjusted_dist.pdf, min_theta, max_theta)
        axes.text(0.6, 0.6, f"Unadjusted integral: {unadjusted_integral:.2f}\nAdjusted integral: {adjusted_integral:.2f}", transform=axes.transAxes)

        plt.xlim([min_theta, max_theta])  # Set x-axis limits
        plt.xlabel(r"$\theta_{site_%d}$"%(j+1))
        plt.ylabel("Density")
        # plt.title(r"Density of $\theta_{site_%d}$ for iteration %d"%(j+1, i))
        plt.title(r"Density of $\theta_{site_%d}$ for truncated normal methods"%(j+1))
        if j in [0,1]:
            plt.ylim([0, 120])
        plt.legend()
        fig.savefig(plotdir + 'theta_site_%d_iter_%d.png'%(j+1, i), dpi = 100)
        plt.close()

        fig, axes = plt.subplots(1, 1, figsize = (8,6))
        # sns.kdeplot(gamma_samples, label="Unadjusted", shade=True, clip=(0, None), color='blue')
        # sns.kdeplot(results['collected_ensembles'][i][:, j+size],  label="Adjusted", shade=True, clip=(0, None), color='red')
        a, b = (0 - np.mean(gamma_samples)) / np.std(gamma_samples), np.inf
        unadjusted_dist_gamma = truncnorm(a, b, loc=np.mean(gamma_samples), scale=np.std(gamma_samples))
        a, b = (0 - np.mean(results['collected_ensembles'][i][:, j+size])) / np.std(results['collected_ensembles'][i][:, j+size]), np.inf
        adjusted_dist_gamma = truncnorm(a, b, loc=np.mean(results['collected_ensembles'][i][:, j+size]), scale=np.std(results['collected_ensembles'][i][:, j+size]))
        x = np.linspace(min_gamma, max_gamma, 1000)
        axes.fill_between(x, unadjusted_dist.pdf(x), alpha=0.5, color='blue')  # plot scipy result as filled area
        axes.plot(x, unadjusted_dist.pdf(x), label="Unadjusted (truncnorm)", color='blue')  # plot scipy result as solid line
        axes.fill_between(x, adjusted_dist.pdf(x), alpha=0.5, color='red')  # plot scipy result as filled area
        axes.plot(x, adjusted_dist.pdf(x), label="Adjusted (truncnorm)", color='red')  # plot scipy result as solid line
        unadjusted_integral, _ = quad(unadjusted_dist.pdf, min_gamma, max_gamma)
        adjusted_integral, _ = quad(adjusted_dist.pdf, min_gamma, max_gamma)
        axes.text(0.6, 0.6, f"Unadjusted integral: {unadjusted_integral:.2f}\nAdjusted integral: {adjusted_integral:.2f}", transform=axes.transAxes)

        plt.xlim([min_gamma, max_gamma])  # Set x-axis limits
        plt.xlabel(r"$\gamma_{site_%d}$"%(j+1))
        plt.ylabel("Density")
        # plt.title(r"Density of $\gamma_{site_%d}$ for iteration %d"%(j+1, i))
        plt.title(r"Density of $\gamma_{site_%d}$ for truncated normal methods"%(j+1))
        plt.legend()
        fig.savefig(plotdir + 'gamma_site_%d_iter_%d.png'%(j+1, i), dpi = 100)
        plt.close()
    else:
        fig, axes = plt.subplots(1, 1, figsize = (8,6))
        # sns.kdeplot(theta_samples, label="Unadjusted", shade=True, clip=(0, None), color='blue')
        a, b = (0 - np.mean(theta_samples)) / np.std(theta_samples), np.inf
        unadjusted_dist = truncnorm(a, b, loc=np.mean(theta_samples), scale=np.std(theta_samples))
        x = np.linspace(min_theta, max_theta, 1000)
        axes.plot(x, unadjusted_dist.pdf(x), label="Unadjusted (truncnorm)", color='blue')  # plot scipy result as dashed
        axes.fill_between(x, unadjusted_dist.pdf(x), color='blue', alpha=0.3)  # Shaded area for unadjusted
        sns.kdeplot(results['collected_ensembles'][i][:, j],  label="Adjusted", shade=True, clip=(0, None), color='red',bw_adjust=5)
        plt.xlim([min_theta, max_theta])  # Set x-axis limits
        plt.xlabel(r"$\theta_{site_%d}$"%(j+1))
        plt.ylabel("Density")
        # plt.title(r"Density of $\theta_{site_%d}$ for iteration %d"%(j+1, i))
        plt.title(r"Density of $\theta_{site_%d}$ for reflection boundary methods"%(j+1))
        if j in [0,1]:
            plt.ylim([0, 120])
        plt.legend()
        fig.savefig(plotdir + 'theta_site_%d_iter_%d.png'%(j+1, i), dpi = 100)
        plt.close()

        fig, axes = plt.subplots(1, 1, figsize = (8,6))
        # sns.kdeplot(gamma_samples, label="Unadjusted", shade=True, clip=(0, None), color='blue')
        a, b = (0 - np.mean(gamma_samples)) / np.std(gamma_samples), np.inf
        unadjusted_dist_gamma = truncnorm(a, b, loc=np.mean(gamma_samples), scale=np.std(gamma_samples))
        x = np.linspace(min_theta, max_theta, 1000)
        axes.plot(x, unadjusted_dist.pdf(x), label="Unadjusted (truncnorm)", color='blue')  # plot scipy result as dashed
        axes.fill_between(x, unadjusted_dist.pdf(x), color='blue', alpha=0.3)  # Shaded area for unadjusted
        sns.kdeplot(results['collected_ensembles'][i][:, j+size],  label="Adjusted", shade=True, clip=(0, None), color='red',bw_adjust=3)
        plt.xlim([min_gamma, max_gamma])  # Set x-axis limits
        plt.xlabel(r"$\gamma_{site_%d}$"%(j+1))
        plt.ylabel("Density")
        # plt.title(r"Density of $\gamma_{site_%d}$ for iteration %d"%(j+1, i))
        plt.title(r"Density of $\gamma_{site_%d}$ for reflection boundary methods"%(j+1))
        plt.legend()
        fig.savefig(plotdir + 'gamma_site_%d_iter_%d.png'%(j+1, i), dpi = 100)
        plt.close()

        fig, axes = plt.subplots(1, 1, figsize = (8,6))
        # sns.kdeplot(theta_samples, label="Unadjusted", shade=True, clip=(0, None), color='blue')
        # sns.kdeplot(results['collected_ensembles'][i][:, j],  label="Adjusted", shade=True, clip=(0, None), color='red')
        a, b = (0 - np.mean(theta_samples)) / np.std(theta_samples), np.inf
        unadjusted_dist = truncnorm(a, b, loc=np.mean(theta_samples), scale=np.std(theta_samples))
        a, b = (0 - np.mean(results['collected_ensembles'][i][:, j])) / np.std(results['collected_ensembles'][i][:, j]), np.inf
        adjusted_dist = truncnorm(a, b, loc=np.mean(results['collected_ensembles'][i][:, j]), scale=np.std(results['collected_ensembles'][i][:, j]))
        x = np.linspace(min_theta, max_theta, 1000)
        axes.plot(x, unadjusted_dist.pdf(x), label="Unadjusted (truncnorm)", color='blue')  # plot scipy result as dashed
        axes.fill_between(x, unadjusted_dist.pdf(x), color='blue', alpha=0.3)  # Shaded area for unadjusted
        axes.plot(x, adjusted_dist.pdf(x), label="Adjusted (truncnorm)", color='red')  # plot scipy result as dashed
        axes.fill_between(x, adjusted_dist.pdf(x), color='red', alpha=0.3) 
        unadjusted_integral, _ = quad(unadjusted_dist.pdf, min_theta, max_theta)
        adjusted_integral, _ = quad(adjusted_dist.pdf, min_theta, max_theta)
        axes.text(0.6, 0.6, f"Unadjusted integral: {unadjusted_integral:.2f}\nAdjusted integral: {adjusted_integral:.2f}", transform=axes.transAxes)

        plt.xlim([min_theta, max_theta])  # Set x-axis limits
        plt.xlabel(r"$\theta_{site_%d}$"%(j+1))
        plt.ylabel("Density")
        # plt.title(r"Density of $\theta_{site_%d}$ for iteration %d"%(j+1, i))
        plt.title(r"Density of $\theta_{site_%d}$ for reflection boundary methods"%(j+1))
        if j in [0,1]:
            plt.ylim([0, 120])
        plt.legend()
        fig.savefig(plotdir + 'theta_site_%d_iter_%d_truncnormal.png'%(j+1, i), dpi = 100)
        plt.close()

        fig, axes = plt.subplots(1, 1, figsize = (8,6))
        # sns.kdeplot(gamma_samples, label="Unadjusted", shade=True, clip=(0, None), color='blue')
        # sns.kdeplot(results['collected_ensembles'][i][:, j+size],  label="Adjusted", shade=True, clip=(0, None), color='red')
        a, b = (0 - np.mean(gamma_samples)) / np.std(gamma_samples), np.inf
        unadjusted_dist_gamma = truncnorm(a, b, loc=np.mean(gamma_samples), scale=np.std(gamma_samples))
        a, b = (0 - np.mean(results['collected_ensembles'][i][:, j+size])) / np.std(results['collected_ensembles'][i][:, j+size]), np.inf
        adjusted_dist_gamma = truncnorm(a, b, loc=np.mean(results['collected_ensembles'][i][:, j+size]), scale=np.std(results['collected_ensembles'][i][:, j+size]))
        x = np.linspace(min_gamma, max_gamma, 1000)
        axes.fill_between(x, unadjusted_dist.pdf(x), alpha=0.5, color='blue')  # plot scipy result as filled area
        axes.plot(x, unadjusted_dist.pdf(x), label="Unadjusted (truncnorm)", color='blue')  # plot scipy result as solid line
        axes.fill_between(x, adjusted_dist.pdf(x), alpha=0.5, color='red')  # plot scipy result as filled area
        axes.plot(x, adjusted_dist.pdf(x), label="Adjusted (truncnorm)", color='red')  # plot scipy result as solid line
        unadjusted_integral, _ = quad(unadjusted_dist.pdf, min_gamma, max_gamma)
        adjusted_integral, _ = quad(adjusted_dist.pdf, min_gamma, max_gamma)
        axes.text(0.6, 0.6, f"Unadjusted integral: {unadjusted_integral:.2f}\nAdjusted integral: {adjusted_integral:.2f}", transform=axes.transAxes)

        plt.xlim([min_gamma, max_gamma])  # Set x-axis limits
        plt.xlabel(r"$\gamma_{site_%d}$"%(j+1))
        plt.ylabel("Density")
        # plt.title(r"Density of $\gamma_{site_%d}$ for iteration %d"%(j+1, i))
        plt.title(r"Density of $\gamma_{site_%d}$ for reflection boundary methods"%(j+1))
        plt.legend()
        fig.savefig(plotdir + 'gamma_site_%d_iter_%d_truncnormal.png'%(j+1, i), dpi = 100)
        plt.close()

    if mode == 2.0:
        fig, ax1 = plt.subplots(1, 1, figsize = (8,6))
        sns.histplot(theta_samples, bins=100, label="Unadjusted", kde=False, color='blue', ax=ax1)
        ax1.set_ylabel('Count (Unadjusted)')
        ax2 = ax1.twinx()
        sns.histplot(results['collected_ensembles'][i][:, j], bins=100, label="Adjusted", kde=False, color='red', ax=ax2)
        ax2.set_ylabel('Count (Adjusted)')
        plt.xlim([min_theta, max_theta])  # Set x-axis limits
        plt.xlabel(r"$\theta_{site_%d}$"%(j+1))
        # plt.title(r"Density of $\theta_{site_%d}$ for iteration %d"%(j+1, i))
        plt.title(r"Distribution of $\theta_{site_%d}$ for truncated normal methods"%(j+1))
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc=0)
        ax1.grid(False)
        ax2.grid(False)
        fig.savefig(plotdir + 'theta_site_%d_iter_%d_untruncated_hist.png'%(j+1, i), dpi = 100)
        plt.close()

        fig, axes = plt.subplots(1, 1, figsize = (8,6))
        sns.kdeplot(theta_samples, label="Unadjusted", shade=True, color='blue',bw_adjust=3)
        sns.kdeplot(results['collected_ensembles'][i][:, j],  label="Adjusted", shade=True, color='red',bw_adjust=3)
        plt.xlim([min_theta, max_theta])  # Set x-axis limits
        plt.xlabel(r"$\theta_{site_%d}$"%(j+1))
        plt.ylabel("Density")
        # plt.title(r"Density of $\theta_{site_%d}$ for iteration %d"%(j+1, i))
        plt.title(r"Density of $\theta_{site_%d}$ for truncated normal methods"%(j+1))
        if j in [0,1]:
            plt.ylim([0, 120])
        plt.legend()
        fig.savefig(plotdir + 'theta_site_%d_iter_%d_untruncated.png'%(j+1, i), dpi = 100)
        plt.close()

        fig, ax1 = plt.subplots(1, 1, figsize = (8,6))
        sns.histplot(gamma_samples, bins=100, label="Unadjusted", kde=False, color='blue', ax=ax1)
        ax1.set_ylabel('Count (Unadjusted)')
        ax2 = ax1.twinx()
        sns.histplot(results['collected_ensembles'][i][:, j+size], bins=100, label="Adjusted", kde=False, color='red', ax=ax2)
        ax2.set_ylabel('Count (Adjusted)')
        plt.xlim([min_gamma, max_gamma])  # Set x-axis limits
        plt.xlabel(r"$\gamma_{site_%d}$"%(j+1))
        # plt.title(r"Density of $\gamma_{site_%d}$ for iteration %d"%(j+1, i))
        plt.title(r"Distribution of $\gamma_{site_%d}$ for truncated normal methods"%(j+1))
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc=0)
        ax1.grid(False)
        ax2.grid(False)
        fig.savefig(plotdir + 'gamma_site_%d_iter_%d_untruncated_hist.png'%(j+1, i), dpi = 100)
        plt.close()

        fig, axes = plt.subplots(1, 1, figsize = (8,6))
        sns.kdeplot(gamma_samples, label="Unadjusted", shade=True, color='blue',bw_adjust=3)
        sns.kdeplot(results['collected_ensembles'][i][:, j+size],  label="Adjusted", shade=True, color='red',bw_adjust=3)
        plt.xlim([min_gamma, max_gamma])  # Set x-axis limits
        plt.xlabel(r"$\gamma_{site_%d}$"%(j+1))
        plt.ylabel("Density")
        # plt.title(r"Density of $\gamma_{site_%d}$ for iteration %d"%(j+1, i))
        plt.title(r"Density of $\gamma_{site_%d}$ for truncated normal methods"%(j+1))
        plt.legend()
        fig.savefig(plotdir + 'gamma_site_%d_iter_%d_untruncated.png'%(j+1, i), dpi = 100)
        plt.close()

    if mode == 3.0:

        from sklearn.neighbors import KernelDensity

        fig, axes = plt.subplots(1, 1, figsize = (8,6))
        a, b = (0 - np.mean(theta_samples)) / np.std(theta_samples), np.inf
        unadjusted_dist = truncnorm(a, b, loc=np.mean(theta_samples), scale=np.std(theta_samples))

        data = results['collected_ensembles'][i][:, j]
        p_zero = np.mean(data < 5e-3)
        data_non_zero = data[data >= 5e-3]

        # Fit a kernel density estimate to the non-zero data
        kde = KernelDensity(kernel='gaussian', bandwidth=0.5).fit(data_non_zero[:, None])

        x = np.linspace(min(min_theta, min(data)), max(max_theta, max(data)), 1000)
        axes.plot(x, unadjusted_dist.pdf(x), label="Unadjusted (truncnorm)", color='blue')  # plot scipy result as dashed
        axes.fill_between(x, unadjusted_dist.pdf(x), color='blue', alpha=0.3)  # Shaded area for unadjusted

        pdf_vals_inflated = np.exp(kde.score_samples(x[:, None]))
        pdf_vals_inflated = p_zero * (x < 5e-3) + (1 - p_zero) * pdf_vals_inflated
        axes.plot(x, pdf_vals_inflated, label='Adjusted (Zero-Inflated KDE)', color='red')
        axes.fill_between(x, pdf_vals_inflated, color='red', alpha=0.3)

        plt.xlim([min(min_theta, min(data)), max(max_theta, max(data))])  # Set x-axis limits
        plt.xlabel(r"$\theta_{site_%d}$"%(j+1))
        plt.ylabel("Density")
        plt.title(r"Density of $\theta_{site_%d}$ for reflection boundary methods"%(j+1))
        if j in [0,1]:
            plt.ylim([0, 120])
        plt.legend()
        fig.savefig(plotdir + 'theta_site_%d_inflated.png'%(j+1), dpi = 100)
        plt.close()






# size = results['size']
# np.random.seed(256)
# for j in range(size):

#     num_samples = len(results['collected_ensembles'][len(results['collected_ensembles'])-1][:, j])
#     mu = theta[j]  # Assuming theta is your mean array
#     sigma = thetaSD[j]  # Assuming thetaSD is your standard deviation array
#     theta_samples = np.random.normal(mu, sigma, 50000)

#     mu = gamma[j]  # Assuming gamma is your mean array
#     sigma = gammaSD[j]  # Assuming gammaSD is your standard deviation array
#     gamma_samples = np.random.normal(mu, sigma, 50000)
    
#     # Find min and max across all iterations for the same site
#     min_theta = np.min([np.min(results['collected_ensembles'][i][:, j]) for i in range(len(results['collected_ensembles']))]+ [np.min(theta_samples)])
#     max_theta = np.max([np.max(results['collected_ensembles'][i][:, j]) for i in range(len(results['collected_ensembles']))]+ [np.max(theta_samples)])

#     min_gamma = np.min([np.min(results['collected_ensembles'][i][:, j + size]) for i in range(len(results['collected_ensembles']))]+ [np.min(gamma_samples)])
#     max_gamma = np.max([np.max(results['collected_ensembles'][i][:, j + size]) for i in range(len(results['collected_ensembles']))]+ [np.max(gamma_samples)])


#     # for i in range(len(results['collected_ensembles'])):
#     i = len(results['sol_val_Z_tracker'])-1
#     # i = 0
#         # For theta parameters
#     fig, axes = plt.subplots(1, 1, figsize = (8,6))
#     # sns.histplot(theta_samples, bins=100, label="Unadjusted", kde=True, color='blue')
#     # sns.histplot(results['collected_ensembles'][i][:, j], bins=100, label="Adjusted", kde=True, color='red')
#     sns.kdeplot(theta_samples, label="Unadjusted", shade=True, clip=(0, None), color='blue')
#     sns.kdeplot(results['collected_ensembles'][i][:, j],  label="Adjusted", shade=True, clip=(0, None), color='red')
#     plt.xlim([min_theta, max_theta])  # Set x-axis limits

#     plt.xlabel(r"$\theta_{site_%d}$"%(j+1))
#     plt.ylabel("Density")
#     plt.title(r"Density of $\theta_{site_%d}$ for iteration %d"%(j+1, i))
#     if j in [0,1]:
#         plt.ylim([0, 120])
#     plt.legend()
#     fig.savefig(plotdir + 'theta_site_%d_iter_%d.png'%(j+1, i), dpi = 100)
#     plt.close()

#     # For gamma parameters
#     fig, axes = plt.subplots(1, 1, figsize = (8,6))
#     sns.kdeplot(gamma_samples, label="Unadjusted", shade=True, clip=(0, None), color='blue')
#     sns.kdeplot(results['collected_ensembles'][i][:, j+size],  label="Adjusted", shade=True, clip=(0, None), color='red')
#     plt.xlim([min_gamma, max_gamma])  # Set x-axis limits

#     plt.xlabel(r"$\gamma_{site_%d}$"%(j+1))
#     plt.ylabel("Density")
#     plt.title(r"Density of $\gamma_{site_%d}$ for iteration %d"%(j+1, i))
#     plt.legend()
#     fig.savefig(plotdir + 'gamma_site_%d_iter_%d.png'%(j+1, i), dpi = 100)
#     plt.close()

#     if mode == 2.0:
#         fig, axes = plt.subplots(1, 1, figsize = (8,6))
#         # sns.histplot(theta_samples, bins=100, label="Unadjusted", kde=True, color='blue')
#         # sns.histplot(results['collected_ensembles'][i][:, j], bins=100, label="Adjusted", kde=True, color='red')
#         sns.kdeplot(theta_samples[theta_samples>0], label="Unadjusted", shade=True, color='blue')
#         sns.kdeplot(results['collected_ensembles'][i][:, j][results['collected_ensembles'][i][:, j]>0],  label="Adjusted", shade=True, color='red')
#         plt.xlim([min_theta, max_theta])  # Set x-axis limits

#         plt.xlabel(r"$\theta_{site_%d}$"%(j+1))
#         plt.ylabel("Density")
#         plt.title(r"Density of $\theta_{site_%d}$ for iteration %d"%(j+1, i))
#         if j in [0,1]:
#             plt.ylim([0, 120])
#         plt.legend()
#         fig.savefig(plotdir + 'theta_site_%d_iter_%d_untruncated.png'%(j+1, i), dpi = 100)
#         plt.close()

#         # For gamma parameters
#         fig, axes = plt.subplots(1, 1, figsize = (8,6))
#         sns.kdeplot(gamma_samples[gamma_samples>0], label="Unadjusted", shade=True, color='blue')
#         sns.kdeplot(results['collected_ensembles'][i][:, j+size][results['collected_ensembles'][i][:, j+size]>0],  label="Adjusted", shade=True, color='red')
#         plt.xlim([min_gamma, max_gamma])  # Set x-axis limits

#         plt.xlabel(r"$\gamma_{site_%d}$"%(j+1))
#         plt.ylabel("Density")
#         plt.title(r"Density of $\gamma_{site_%d}$ for iteration %d"%(j+1, i))
#         plt.legend()
#         fig.savefig(plotdir + 'gamma_site_%d_iter_%d_untruncated.png'%(j+1, i), dpi = 100)
#         plt.close()

