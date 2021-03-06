import numpy as np
from sbe.utility import conditional_njit


##########################################################################################
## Observables working with density matrices that contain NO time data; only path
##########################################################################################
def make_polarization_path(dipole, path, E_dir, P):
    """
    Function that calculates the polarization for the current path

    Parameters:
    -----------
    dipole : Symbolic Dipole
    pathlen : int
        Length of one path
    n_time_steps : int
        Number of time steps
    E_dir : np.ndarray [type_real_np]
        Direction of the electric field
    A_field : np.ndarray [type_real_np]
        Vector potential integrated from electric field
    gauge : string
        System gauge 'length' or 'velocity'

    Returns:
    --------
    P_E_dir : np.ndarray [type_real_np]
        Polarization in E-field direction
    P_ortho : np.ndarray [type_real_np]
        Polarization orthogonal to E-field direction
    """
    di_01xf = dipole.Axfjit[0][1]
    di_01yf = dipole.Ayfjit[0][1]

    E_ort = np.array([E_dir[1], -E_dir[0]])
    kx_in_path_before_shift = path[:, 0]
    ky_in_path_before_shift = path[:, 1]
    pathlen = kx_in_path_before_shift.size

    type_complex_np = P.type_complex_np
    gauge = P.gauge
    @conditional_njit(type_complex_np)
    def polarization_path(rho_cv, A_field):
        ##################################################
        # Dipole container
        ##################################################
        d_01x = np.empty(pathlen, dtype=type_complex_np)
        d_01y = np.empty(pathlen, dtype=type_complex_np)

        d_E_dir = np.empty(pathlen, dtype=type_complex_np)
        d_ortho = np.empty(pathlen, dtype=type_complex_np)

        if gauge == 'length':
            kx_shift = 0
            ky_shift = 0
        if gauge == 'velocity':
            kx_shift = A_field*E_dir[0]
            ky_shift = A_field*E_dir[1]

        kx_in_path = kx_in_path_before_shift + kx_shift
        ky_in_path = ky_in_path_before_shift + ky_shift

        d_01x[:] = di_01xf(kx=kx_in_path, ky=ky_in_path)
        d_01y[:] = di_01yf(kx=kx_in_path, ky=ky_in_path)

        d_E_dir[:] = d_01x * E_dir[0] + d_01y * E_dir[1]
        d_ortho[:] = d_01x * E_ort[0] + d_01y * E_ort[1]

        P_E_dir = 2*np.real(np.sum(d_E_dir * rho_cv))
        P_ortho = 2*np.real(np.sum(d_ortho * rho_cv))

        return P_E_dir, P_ortho

    return polarization_path


def make_current_path(sys, path, E_dir, curvature, P):
    '''
    Calculates the intraband current as: J(t) = sum_k sum_n [j_n(k)f_n(k,t)]
    where j_n(k) != (d/dk) E_n(k)

    Parameters
    ----------
    sys : TwoBandSystem
        Hamiltonian and related functions
    pathlen : int
        Length of one path
    n_time_steps : int
        Number of time steps
    E_dir : np.ndarray [type_real_np]
        Direction of the electric field
    A_field : np.ndarray [type_real_np]
        Vector potential integrated from electric field
    gauge : string
        System gauge 'length' or 'velocity'

    Returns
    -------
    J_E_dir : np.ndarray [type_real_np]
        intraband current j_intra in E-field direction
    J_ortho : np.ndarray [type_real_np]
        intraband current j_intra orthogonal to E-field direction
    '''
    edxjit_v = sys.ederivfjit[0]
    edyjit_v = sys.ederivfjit[1]
    edxjit_c = sys.ederivfjit[2]
    edyjit_c = sys.ederivfjit[3]

    if P.save_anom:
        Bcurv_00 = curvature.Bfjit[0][0]
        Bcurv_11 = curvature.Bfjit[1][1]

    E_ort = np.array([E_dir[1], -E_dir[0]])
    kx_in_path_before_shift = path[:, 0]
    ky_in_path_before_shift = path[:, 1]
    pathlen = kx_in_path_before_shift.size

    type_real_np = P.type_real_np
    type_complex_np = P.type_complex_np
    gauge = P.gauge
    save_anom = P.save_anom
    @conditional_njit(type_complex_np)
    def current_path(rho_vv, rho_cc, A_field, E_field):
        ##################################################
        # E derivative container
        ##################################################
        edx_v = np.empty(pathlen, dtype=type_real_np)
        edy_v = np.empty(pathlen, dtype=type_real_np)
        edx_c = np.empty(pathlen, dtype=type_real_np)
        edy_c = np.empty(pathlen, dtype=type_real_np)

        e_deriv_E_dir_v = np.empty(pathlen, dtype=type_real_np)
        e_deriv_ortho_v = np.empty(pathlen, dtype=type_real_np)
        e_deriv_E_dir_c = np.empty(pathlen, dtype=type_real_np)
        e_deriv_ortho_c = np.empty(pathlen, dtype=type_real_np)

        if gauge == 'length':
            kx_shift = 0
            ky_shift = 0
            rho_vv_subs = 0
        if gauge == 'velocity':
            kx_shift = A_field*E_dir[0]
            ky_shift = A_field*E_dir[1]
            rho_vv_subs = 1

        kx_in_path = kx_in_path_before_shift + kx_shift
        ky_in_path = ky_in_path_before_shift + ky_shift

        edx_v[:] = edxjit_v(kx=kx_in_path, ky=ky_in_path)
        edy_v[:] = edyjit_v(kx=kx_in_path, ky=ky_in_path)
        edx_c[:] = edxjit_c(kx=kx_in_path, ky=ky_in_path)
        edy_c[:] = edyjit_c(kx=kx_in_path, ky=ky_in_path)


        e_deriv_E_dir_v[:] = edx_v * E_dir[0] + edy_v * E_dir[1]
        e_deriv_ortho_v[:] = edx_v * E_ort[0] + edy_v * E_ort[1]
        e_deriv_E_dir_c[:] = edx_c * E_dir[0] + edy_c * E_dir[1]
        e_deriv_ortho_c[:] = edx_c * E_ort[0] + edy_c * E_ort[1]

        J_E_dir = - np.sum(e_deriv_E_dir_v * (rho_vv.real - rho_vv_subs)) - \
            np.sum(e_deriv_E_dir_c * rho_cc.real)
        J_ortho = - np.sum(e_deriv_ortho_v * (rho_vv.real - rho_vv_subs)) - \
            np.sum(e_deriv_ortho_c * rho_cc.real)

        if save_anom:
            Bcurv_v = np.empty(pathlen, dtype=type_complex_np)
            Bcurv_c = np.empty(pathlen, dtype=type_complex_np)

            Bcurv_v = Bcurv_00(kx=kx_in_path, ky=ky_in_path)
            Bcurv_c = Bcurv_11(kx=kx_in_path, ky=ky_in_path)

            J_anom_ortho = -E_field * np.sum(Bcurv_v.real * rho_vv.real)
            J_anom_ortho = -E_field * np.sum(Bcurv_c.real * rho_cc.real)
        else:
            J_anom_ortho = 0

        return J_E_dir, J_ortho, J_anom_ortho

    return current_path


def make_emission_exact_path_velocity(sys, path, E_dir, curvature, P):
    """
    Construct a function that calculates the emission for the system solution per path
    Works for velocity gauge.

    Parameters
    ----------
    sys : TwoBandSystem
        Hamiltonian and related functions
    path : np.ndarray [type_real_np]
        kx and ky components of path
    E_dir : np.ndarray [type_real_np]
        Direction of the electric field
    do_semicl : bool
        if semiclassical calculation should be done
    curvature : SymbolicCurvature
        Curvature is only needed for semiclassical calculation

    Returns
    -------
    emision_kernel : function
        Calculates per timestep current of a path
    """

    hderivx = sys.hderivfjit[0]
    hdx_00 = hderivx[0][0]
    hdx_01 = hderivx[0][1]
    hdx_10 = hderivx[1][0]
    hdx_11 = hderivx[1][1]

    hderivy = sys.hderivfjit[1]
    hdy_00 = hderivy[0][0]
    hdy_01 = hderivy[0][1]
    hdy_10 = hderivy[1][0]
    hdy_11 = hderivy[1][1]

    Ujit = sys.Ujit
    U_00 = Ujit[0][0]
    U_01 = Ujit[0][1]
    U_10 = Ujit[1][0]
    U_11 = Ujit[1][1]

    Ujit_h = sys.Ujit_h
    U_h_00 = Ujit_h[0][0]
    U_h_01 = Ujit_h[0][1]
    U_h_10 = Ujit_h[1][0]
    U_h_11 = Ujit_h[1][1]

    if P.do_semicl:
        Bcurv_00 = curvature.Bfjit[0][0]
        Bcurv_11 = curvature.Bfjit[1][1]

    E_ort = np.array([E_dir[1], -E_dir[0]])

    kx_in_path_before_shift = path[:, 0]
    ky_in_path_before_shift = path[:, 1]
    pathlen = kx_in_path_before_shift.size

    type_complex_np = P.type_complex_np
    symmetric_insulator = P.symmetric_insulator
    do_semicl = P.do_semicl
    @conditional_njit(type_complex_np)
    def emission_exact_path_velocity(solution, E_field, A_field):
        '''
        Calculates current from the system density matrix

        Parameters:
        -----------
        solution : np.ndarray [type_complex_np]
            Per timestep solution, idx 0 is k; idx 1 is fv, pvc, pcv, fc
        E_field : type_real_np
            Per timestep E_field
        A_field : type_real_np
            In the velocity gauge this determines the k-shift

        Returns:
        --------
        I_E_dir : type_real_np
            Parallel to electric field component of current
        I_ortho : type_real_np
            Orthogonal to electric field component of current
        '''
        ##########################################################
        # H derivative container
        ##########################################################
        h_deriv_x = np.empty((pathlen, 2, 2), dtype=type_complex_np)
        h_deriv_y = np.empty((pathlen, 2, 2), dtype=type_complex_np)
        h_deriv_E_dir = np.empty((pathlen, 2, 2), dtype=type_complex_np)
        h_deriv_ortho = np.empty((pathlen, 2, 2), dtype=type_complex_np)

        ##########################################################
        # Wave function container
        ##########################################################
        U = np.empty((pathlen, 2, 2), dtype=type_complex_np)
        U_h = np.empty((pathlen, 2, 2), dtype=type_complex_np)

        ##########################################################
        # Berry curvature container
        ##########################################################
        if do_semicl:
            Bcurv = np.empty((pathlen, 2), dtype=type_complex_np)

        kx_in_path = kx_in_path_before_shift + A_field*E_dir[0]
        ky_in_path = ky_in_path_before_shift + A_field*E_dir[1]

        h_deriv_x[:, 0, 0] = hdx_00(kx=kx_in_path, ky=ky_in_path)
        h_deriv_x[:, 0, 1] = hdx_01(kx=kx_in_path, ky=ky_in_path)
        h_deriv_x[:, 1, 0] = hdx_10(kx=kx_in_path, ky=ky_in_path)
        h_deriv_x[:, 1, 1] = hdx_11(kx=kx_in_path, ky=ky_in_path)

        h_deriv_y[:, 0, 0] = hdy_00(kx=kx_in_path, ky=ky_in_path)
        h_deriv_y[:, 0, 1] = hdy_01(kx=kx_in_path, ky=ky_in_path)
        h_deriv_y[:, 1, 0] = hdy_10(kx=kx_in_path, ky=ky_in_path)
        h_deriv_y[:, 1, 1] = hdy_11(kx=kx_in_path, ky=ky_in_path)

        h_deriv_E_dir[:, :, :] = h_deriv_x*E_dir[0] + h_deriv_y*E_dir[1]
        h_deriv_ortho[:, :, :] = h_deriv_x*E_ort[0] + h_deriv_y*E_ort[1]

        U[:, 0, 0] = U_00(kx=kx_in_path, ky=ky_in_path)
        U[:, 0, 1] = U_01(kx=kx_in_path, ky=ky_in_path)
        U[:, 1, 0] = U_10(kx=kx_in_path, ky=ky_in_path)
        U[:, 1, 1] = U_11(kx=kx_in_path, ky=ky_in_path)

        U_h[:, 0, 0] = U_h_00(kx=kx_in_path, ky=ky_in_path)
        U_h[:, 0, 1] = U_h_01(kx=kx_in_path, ky=ky_in_path)
        U_h[:, 1, 0] = U_h_10(kx=kx_in_path, ky=ky_in_path)
        U_h[:, 1, 1] = U_h_11(kx=kx_in_path, ky=ky_in_path)

        if do_semicl:
            Bcurv[:, 0] = Bcurv_00(kx=kx_in_path, ky=ky_in_path)
            Bcurv[:, 1] = Bcurv_11(kx=kx_in_path, ky=ky_in_path)

        I_E_dir = 0
        I_ortho = 0

        rho_vv = solution[:, 0]
        # rho_vc = solution[:, 1]
        rho_cv = solution[:, 2]
        rho_cc = solution[:, 3]

        if symmetric_insulator:
            rho_vv = -rho_cc + 1

        for i_k in range(pathlen):

            dH_U_E_dir = h_deriv_E_dir[i_k] @ U[i_k]
            U_h_H_U_E_dir = U_h[i_k] @ dH_U_E_dir

            dH_U_ortho = h_deriv_ortho[i_k] @ U[i_k]
            U_h_H_U_ortho = U_h[i_k] @ dH_U_ortho

            I_E_dir += - U_h_H_U_E_dir[0, 0].real * (rho_vv[i_k].real - 1)
            I_E_dir += - U_h_H_U_E_dir[1, 1].real * rho_cc[i_k].real
            I_E_dir += - 2*np.real(U_h_H_U_E_dir[0, 1] * rho_cv[i_k])

            I_ortho += - U_h_H_U_ortho[0, 0].real * (rho_vv[i_k].real - 1)
            I_ortho += - U_h_H_U_ortho[1, 1].real * rho_cc[i_k].real
            I_ortho += - 2*np.real(U_h_H_U_ortho[0, 1] * rho_cv[i_k])

            if do_semicl:
                # '-' because there is q^2 compared to q only at the SBE current
                I_ortho += -E_field * Bcurv[i_k, 0].real * rho_vv[i_k].real
                I_ortho += -E_field * Bcurv[i_k, 1].real * rho_cc[i_k].real

        return I_E_dir, I_ortho

    return emission_exact_path_velocity


def make_emission_exact_path_length(sys, path, E_dir, curvature, P):
    """
    Construct a function that calculates the emission for the system solution per path.
    Works for length gauge.

    Parameters
    ----------
    sys : TwoBandSystem
        Hamiltonian and related functions
    path : np.ndarray [type_real_np]
        kx and ky components of path
    E_dir : np.ndarray [type_real_np]
        Direction of the electric field
    do_semicl : bool
        if semiclassical calculation should be done
    curvature : SymbolicCurvature
        Curvature is only needed for semiclassical calculation

    Returns:
    --------
    emission_kernel : function
        Calculates per timestep current of a path
    """

    E_ort = np.array([E_dir[1], -E_dir[0]])

    kx_in_path = path[:, 0]
    ky_in_path = path[:, 1]
    pathlen = kx_in_path.size

    ##########################################################
    # H derivative container
    ##########################################################
    h_deriv_x = np.empty((pathlen, 2, 2), dtype=P.type_complex_np)
    h_deriv_y = np.empty((pathlen, 2, 2), dtype=P.type_complex_np)
    h_deriv_E_dir = np.empty((pathlen, 2, 2), dtype=P.type_complex_np)
    h_deriv_ortho = np.empty((pathlen, 2, 2), dtype=P.type_complex_np)

    ##########################################################
    # Wave function container
    ##########################################################
    U = np.empty((pathlen, 2, 2), dtype=P.type_complex_np)
    U_h = np.empty((pathlen, 2, 2), dtype=P.type_complex_np)

    ##########################################################
    # Berry curvature container
    ##########################################################
    if P.do_semicl:
        Bcurv = np.empty((pathlen, 2), dtype=P.type_complex_np)

    h_deriv_x[:, 0, 0] = sys.hderivfjit[0][0][0](kx=kx_in_path, ky=ky_in_path)
    h_deriv_x[:, 0, 1] = sys.hderivfjit[0][0][1](kx=kx_in_path, ky=ky_in_path)
    h_deriv_x[:, 1, 0] = sys.hderivfjit[0][1][0](kx=kx_in_path, ky=ky_in_path)
    h_deriv_x[:, 1, 1] = sys.hderivfjit[0][1][1](kx=kx_in_path, ky=ky_in_path)

    h_deriv_y[:, 0, 0] = sys.hderivfjit[1][0][0](kx=kx_in_path, ky=ky_in_path)
    h_deriv_y[:, 0, 1] = sys.hderivfjit[1][0][1](kx=kx_in_path, ky=ky_in_path)
    h_deriv_y[:, 1, 0] = sys.hderivfjit[1][1][0](kx=kx_in_path, ky=ky_in_path)
    h_deriv_y[:, 1, 1] = sys.hderivfjit[1][1][1](kx=kx_in_path, ky=ky_in_path)

    h_deriv_E_dir[:, :, :] = h_deriv_x*E_dir[0] + h_deriv_y*E_dir[1]
    h_deriv_ortho[:, :, :] = h_deriv_x*E_ort[0] + h_deriv_y*E_ort[1]

    U[:, 0, 0] = sys.Ujit[0][0](kx=kx_in_path, ky=ky_in_path)
    U[:, 0, 1] = sys.Ujit[0][1](kx=kx_in_path, ky=ky_in_path)
    U[:, 1, 0] = sys.Ujit[1][0](kx=kx_in_path, ky=ky_in_path)
    U[:, 1, 1] = sys.Ujit[1][1](kx=kx_in_path, ky=ky_in_path)

    U_h[:, 0, 0] = sys.Ujit_h[0][0](kx=kx_in_path, ky=ky_in_path)
    U_h[:, 0, 1] = sys.Ujit_h[0][1](kx=kx_in_path, ky=ky_in_path)
    U_h[:, 1, 0] = sys.Ujit_h[1][0](kx=kx_in_path, ky=ky_in_path)
    U_h[:, 1, 1] = sys.Ujit_h[1][1](kx=kx_in_path, ky=ky_in_path)

    if P.do_semicl:
        Bcurv[:, 0] = curvature.Bfjit[0][0](kx=kx_in_path, ky=ky_in_path)
        Bcurv[:, 1] = curvature.Bfjit[1][1](kx=kx_in_path, ky=ky_in_path)

    symmetric_insulator = P.symmetric_insulator
    do_semicl = P.do_semicl
    @conditional_njit(P.type_complex_np)
    def emission_exact_path_length(solution, E_field, _A_field=1):
        '''
        Parameters:
        -----------
        solution : np.ndarray [type_complex_np]
            Per timestep solution, idx 0 is k; idx 1 is fv, pvc, pcv, fc
        E_field : type_real_np
            Per timestep E_field
        _A_field : dummy
            In the length gauge this is just a dummy variable

        Returns:
        --------
        I_E_dir : type_real_np
            Parallel to electric field component of current
        I_ortho : type_real_np
            Orthogonal to electric field component of current
        '''
        I_E_dir = 0
        I_ortho = 0

        rho_vv = solution[:, 0]
        rho_vc = solution[:, 1]
        rho_cv = solution[:, 2]
        rho_cc = solution[:, 3]

        if symmetric_insulator:
            rho_vv = -rho_cc

        for i_k in range(pathlen):

            dH_U_E_dir = h_deriv_E_dir[i_k] @ U[i_k]
            U_h_H_U_E_dir = U_h[i_k] @ dH_U_E_dir

            dH_U_ortho = h_deriv_ortho[i_k] @ U[i_k]
            U_h_H_U_ortho = U_h[i_k] @ dH_U_ortho

            I_E_dir += - U_h_H_U_E_dir[0, 0].real * rho_vv[i_k].real
            I_E_dir += - U_h_H_U_E_dir[1, 1].real * rho_cc[i_k].real
            I_E_dir += - 2*np.real(U_h_H_U_E_dir[0, 1] * rho_cv[i_k])

            I_ortho += - U_h_H_U_ortho[0, 0].real * rho_vv[i_k].real
            I_ortho += - U_h_H_U_ortho[1, 1].real * rho_cc[i_k].real
            I_ortho += - 2*np.real(U_h_H_U_ortho[0, 1] * rho_cv[i_k])

            if do_semicl:
                # '-' because there is q^2 compared to q only at the SBE current
                I_ortho += -E_field * Bcurv[i_k, 0].real * rho_vv[i_k].real
                I_ortho += -E_field * Bcurv[i_k, 1].real * rho_vc[i_k].real

        return I_E_dir, I_ortho

    return emission_exact_path_length
