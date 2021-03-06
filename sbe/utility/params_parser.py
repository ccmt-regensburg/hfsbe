from math import modf
import numpy as np
import sys

from sbe.utility import ConversionFactors as co

def parse_params(user_params):
    class Params():
        pass

    P = Params()
    UP = user_params
    P.user_out = True                       # Command line progress output
    if hasattr(UP, 'user_out'):
        P.user_out = UP.user_out

    P.save_full = False                     # Save full density matrix
    if hasattr(UP, 'save_full'):
        P.save_full = UP.save_full

    P.save_exact = True                     # Save exact result
    if hasattr(UP, 'save_exact'):
        P.save_exact = UP.save_exact

    P.save_approx = False                   # Save j^intra, j^anom, dP^inter/dt
    if hasattr(UP, 'save_approx'):
        P.save_approx = UP.save_approx

    P.save_txt = True                       # Save data as human readable text file
    if hasattr(UP, 'save_txt'):
        P.save_txt = UP.save_txt

    P.do_semicl = False                     # Semiclassical calc. (dipole = 0)
    if hasattr(UP, 'do_semicl'):
        P.do_semicl = UP.do_semicl

    P.gauge = 'length'                      # Gauge of the SBE Dynamics
    if hasattr(UP, 'gauge'):
        P.gauge = UP.gauge

    P.save_anom = False
    if hasattr(UP, 'save_anom'):
        P.save_anom = UP.save_anom

    P.solver_method = 'bdf'                 # 'adams' non-stiff, 'bdf' stiff, 'rk4' Runge-Kutta 4th order
    if hasattr(UP, 'solver_method'):
        P.solver_method = UP.solver_method

    P.precision = 'double'                  # quadruple for reducing numerical noise
    if hasattr(UP, 'precision'):
        P.precision = UP.precision

    if P.precision == 'double':
        P.type_real_np    = np.float64
        P.type_complex_np = np.complex128
    elif P.precision == 'quadruple':
        P.type_real_np    = np.float128
        P.type_complex_np = np.complex256
        if P.solver_method != 'rk4':
            sys.exit("Error: Quadruple precision only works with Runge-Kutta 4 ODE solver.")
    else:
        sys.exit("Only default or quadruple precision available.")

    P.symmetric_insulator = False           # special flag for accurate insulator calc.
    if hasattr(UP, 'symmetric_insulator'):
        P.symmetric_insulator = UP.symmetric_insulator

    P.dk_order = 8
    if hasattr(UP, 'dk_order'):             # Accuracy order of density-matrix k-deriv.
        P.dk_order = UP.dk_order            # with length gauge (avail: 2,4,6,8)
        if P.dk_order not in [2, 4, 6, 8]:
            sys.exit("dk_order needs to be either 2, 4, 6, or 8.")

    # Parameters for initial occupation
    P.e_fermi = UP.e_fermi*co.eV_to_au           # Fermi energy
    P.e_fermi_eV = UP.e_fermi
    P.temperature = UP.temperature*co.eV_to_au   # Temperature
    P.temperature_eV =  UP.temperature

    # Driving field parameters
    P.E0 = UP.E0*co.MVpcm_to_au                  # Driving pulse field amplitude
    P.E0_MVpcm = UP.E0
    P.w = UP.w*co.THz_to_au                      # Driving pulse frequency
    P.w_THz = UP.w
    P.chirp = UP.chirp*co.THz_to_au              # Pulse chirp frequency
    P.chirp_THz = UP.chirp
    P.alpha = UP.alpha*co.fs_to_au               # Gaussian pulse width
    P.alpha_fs = UP.alpha
    P.phase = UP.phase                           # Carrier-envelope phase

    # Time scales
    P.T1 = UP.T1*co.fs_to_au                     # Occupation damping time
    P.gamma1 = 1/P.T1
    P.T1_fs = UP.T1
    P.gamma1_dfs = 1/P.T1_fs

    P.T2 = UP.T2*co.fs_to_au                     # Polarization damping time
    P.gamma2 = 1/P.T2
    P.T2_fs = UP.T2
    P.gamma2_dfs = 1/P.T2_fs

    P.t0 = UP.t0*co.fs_to_au
    P.t0_fs = UP.t0

    P.tf = -P.t0
    P.tf_fs = -P.t0_fs

    P.dt = P.type_real_np(UP.dt*co.fs_to_au)
    P.dt_fs = UP.dt

    Nf = int((abs(2*P.t0_fs))/P.dt_fs)
    if modf((2*P.t0_fs/P.dt_fs))[0] > 1e-12:
        print("WARNING: The time window divided by dt is not an integer.")
    # Define a proper time window if Nt exists
    # +1 assures the inclusion of tf in the calculation
    P.Nt = Nf + 1


    # Brillouin zone type
    P.BZ_type = UP.BZ_type                      # Type of Brillouin zone
    P.Nk1 = UP.Nk1                              # kpoints in b1 direction
    P.Nk2 = UP.Nk2                              # kpoints in b2 direction
    P.Nk = P.Nk1 * P.Nk2

    # special parameters for individual Brillouin zone types
    if P.BZ_type == 'hexagon':
        P.align = UP.align                      # E-field alignment
        P.angle_inc_E_field = None
        P.b1 = UP.b1                                # Reciprocal lattice vectors
        P.b1_dangs = P.b1*co.as_to_au
        P.b2 = UP.b2
        P.b2_dangs = P.b2*co.as_to_au
        P.a = UP.a                                  # Lattice spacing
        P.a_angs = P.a*co.au_to_as
    elif P.BZ_type == 'rectangle':
        P.align = None
        P.angle_inc_E_field = UP.angle_inc_E_field
        P.length_BZ_ortho = UP.length_BZ_ortho
        P.length_BZ_E_dir = UP.length_BZ_E_dir
    else:
        sys.exit("BZ_type needs to be either hexagon or rectangle.")

    P.Nk2_idx_ext = -1
    if hasattr(UP, 'Nk2_idx_ext'):        # For parallelization: only do calculation
        P.Nk2_idx_ext = UP.Nk2_idx_ext    # for path Nk2_idx_ext (in total Nk2 paths)

    # params for n-band solver

    P.dipole_numerics = False
    if hasattr(UP, 'dipole_numerics'):
        P.dipole_numerics = UP.dipole_numerics
        P.n = UP.n
        P.epsilon = UP.epsilon
        P.gidx = UP.gidx

    return P
