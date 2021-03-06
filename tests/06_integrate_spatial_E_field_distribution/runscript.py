import os
import time
import numpy as np
from numpy.fft import *
import multiprocessing
from params import params

import sbe.dipole
import sbe.hamiltonian
from sbe.utility import mkdir_chdir
from sbe.solver import sbe_solver, fourier_current_intensity, gaussian
from sbe.plotting import read_dataset
from sbe.utility import ConversionFactors as co

def dirac():
    A = 0.1974      # Fermi velocity

    dirac_system = sbe.hamiltonian.BiTe(C0=0, C2=0, A=A, R=0, mz=0)
    h_sym, ef_sym, wf_sym, _ediff_sym = dirac_system.eigensystem(gidx=1)
    dirac_dipole = sbe.dipole.SymbolicDipole(h_sym, ef_sym, wf_sym)
    dirac_curvature = sbe.dipole.SymbolicCurvature(h_sym, dirac_dipole.Ax, dirac_dipole.Ay)

    return dirac_system, dirac_dipole, dirac_curvature

def run(system, dipole, curvat):

    num_E_fields = params.num_E_fields
    dist_max     = params.dist_max
    weight       = dist_max / num_E_fields

    dists = np.linspace(weight/2, dist_max-weight/2, num_E_fields)

    E0list = params.E0*np.exp(-dists**2/2)

    ncpus = multiprocessing.cpu_count() - 1

    jobs = []

    for count, E0 in enumerate(E0list):

        params.E0 = E0

        print("\nSTARTED WITH E0 =", E0, "\n")

        mkdir_chdir("E0_"+str(E0))

        p = multiprocessing.Process(target=sbe_solver, args=(system, dipole, params, curvat, ))
        jobs.append(p)
        p.start()
        if (count+1) % ncpus == 0 or count+1 == len(E0list):
            for q in jobs:
                q.join()

        os.chdir('..')

    # collect all the currents from different E-field strenghts
    for count, E0 in enumerate(E0list):

        print("\nSTARTED WITH READING E0 =", E0, "\n")

        Iexactdata, Iapproxdata, Sol = read_dataset("./E0_"+str(E0)+"/")

        # integration weight
        scale_current = weight * dists[count]

        current_time_E_dir = Iexactdata[1] * scale_current
        current_time_ortho = Iexactdata[2] * scale_current

        if count == 0:
            current_time_E_dir_integrated = np.zeros(np.size(current_time_E_dir), dtype=np.float64)
            current_time_ortho_integrated = np.zeros(np.size(current_time_ortho), dtype=np.float64)

        current_time_E_dir_integrated += current_time_E_dir.real
        current_time_ortho_integrated += current_time_ortho.real

    t = Iexactdata[0]
    dt = params.dt*co.fs_to_au
    w = params.w*co.THz_to_au
    alpha = params.alpha*co.fs_to_au

    prefac_emission = 1/(3*(137.036**3))
    freq = fftshift(fftfreq(t.size, d=dt))

    Int_exact_E_dir, Int_exact_ortho, Iw_exact_E_dir, Iw_exact_ortho = fourier_current_intensity(
            current_time_E_dir_integrated, current_time_ortho_integrated,
            gaussian(t, alpha), dt, prefac_emission, freq)

    np.save('Iexact_integrated_over_E_fields', [t,
                           current_time_E_dir_integrated, current_time_ortho_integrated,
                           freq/w, Iw_exact_E_dir, Iw_exact_ortho,
                           Int_exact_E_dir, Int_exact_ortho])

    # dummy test: safe the exact current as approximate current
    np.save('Iapprox_integrated_over_E_fields', [t,
                           current_time_E_dir_integrated, current_time_ortho_integrated,
                           freq/w, Iw_exact_E_dir, Iw_exact_ortho,
                           Int_exact_E_dir, Int_exact_ortho])

if __name__ == "__main__":
    run(*dirac())
