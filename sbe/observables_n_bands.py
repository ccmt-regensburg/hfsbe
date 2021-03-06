import numpy as np
from sbe.utility import ConversionFactors as co
from sbe.dipole import diagonalize, derivative, dipole_elements

# def current_in_path_hderiv(Nk_in_path, num_paths, Nt, density_matrix, n, paths, gidx, epsilon, path_idx):

#     """
#         Calculates the full and intraband current for a given path from eq. (67) in sbe_p01

#         Parameters
#         ----------
#         Nk_in_path : int
#             number of k-points in x-direction (in the path)
#         num_paths : int
#             number of k-points in y-direction (number of paths)
#         Nt : int
#             number of time-steps
#         density_matrix : np.ndarray
#             solution of the semiconductor bloch equation (eq. 51 in sbe_p01)
#         n : int
#             number of bands
#         paths : np.ndarray
#             k-paths in the mesh
#         gidx : int
#             gauge index for the wf-gauge
#         epsilon : float
#             parameter for the derivative
#         path_idx : int
#             index of the current path

#         Returns
#         -------
#         current_in_path : np.ndarray
#             full current of the path with idx path_idx

#     """

#     # derivative dh/dk

#     epsilon = 0.15

#     hgridplusx = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex128)
#     hgridminusx = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex128)
#     hgridplusy = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex128)
#     hgridminusy = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex128)

#     dhdkx = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex128)
#     dhdky = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex128)

#     for i in range(Nk_in_path):
#         for j in range(num_paths):
#             kx = paths[j, i, 0]
#             ky = paths[j, i, 1]
#             hgridplusx[i, j, :, :] = hamiltonian(kx + epsilon, ky)
#             hgridminusx[i, j, :, :] = hamiltonian(kx - epsilon, ky)
#             hgridplusy[i, j, :, :] = hamiltonian(kx, ky + epsilon)
#             hgridminusy[i, j, :, :] = hamiltonian(kx, ky - epsilon)


#     dhdkx = ( hgridplusx -  hgridminusx )/(2*epsilon)
#     dhdky = ( hgridplusy -  hgridminusy )/(2*epsilon)

#     # matrix elements <n k | dh/dk | n' k>

#     matrix_element_x = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex128)
#     matrix_element_y = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex128)

#     for i in range(Nk_in_path):
#         for j in range(num_paths):
#             buff = dhdkx[i,j,:,:] @ wf[i,j,:,:]
#             matrix_element_x[i, j, :, :] = np.conjugate(wf[i, j, :, :].T) @ buff

#             buff = dhdky[i,j,:,:] @ wf[i,j,:,:]
#             matrix_element_y[i, j, :, :] = np.conjugate(wf[i, j, :, :].T) @ buff

#     # full and intraband current via eq. (67) in sbe_p01

#     current_in_path = np.zeros([Nt, 2], dtype=np.complex128)
#     current_in_path_intraband = np.zeros([Nt, 2], dtype=np.complex128)
#     melx = matrix_element_x[:, path_idx, :, :].reshape(Nk_in_path, n**2)
#     mely = matrix_element_y[:, path_idx, :, :].reshape(Nk_in_path, n**2)

#         # n = 2

#     for i_t in range(Nt):
#         #for j in range(n**2):
#         current_in_path[i_t, 0] += - np.sum(melx[:, 0] * density_matrix[:, path_idx, i_t, 0].real)
#         current_in_path[i_t, 1] += - np.sum(mely[:, 0] * density_matrix[:, path_idx, i_t, 0].real)

#         current_in_path[i_t, 0] += - np.sum(melx[:, 3] * density_matrix[:, path_idx, i_t, 3].real)
#         current_in_path[i_t, 1] += - np.sum(mely[:, 3] * density_matrix[:, path_idx, i_t, 3].real)

#         current_in_path_intraband[i_t, :] += current_in_path[i_t, :]

#     for i_t in range(Nt):
#         current_in_path[i_t, 0] += -2*np.sum(np.real(melx[:, 1] * density_matrix[:, path_idx, i_t, 2]))
#         current_in_path[i_t, 1] += -2*np.sum(np.real(mely[:, 1] * density_matrix[:, path_idx, i_t, 2]))

#         # general n

#     #for i_t in range(Nt):           #np.sum(?)
#     #    for j in range(n**2):
#     #        current_in_path[i_t, 0] += np.dot( melx[:, j], density_matrix[:, path_idx, i_t, j])
#     #        current_in_path[i_t, 1] += np.dot( mely[:, j], density_matrix[:, path_idx, i_t, j])

#     return current_in_path, current_in_path_intraband

def make_matrix_elements_hderiv(params, hamiltonian, paths, wf, E_dir, path_idx):

    Nk_in_path = params.Nk1
    num_paths = params.Nk2
    n = params.n
    epsilon = 0.15

    hgridplusx = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex128)
    hgridminusx = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex128)
    hgridplusy = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex128)
    hgridminusy = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex128)

    for i in range(Nk_in_path):
        for j in range(num_paths):
            kx = paths[j, i, 0]
            ky = paths[j, i, 1]
            hgridplusx[i, j, :, :] = hamiltonian(kx=kx+epsilon, ky=ky)
            hgridminusx[i, j, :, :] = hamiltonian(kx=kx-epsilon, ky=ky)
            hgridplusy[i, j, :, :] = hamiltonian(kx=kx, ky=ky+epsilon)
            hgridminusy[i, j, :, :] = hamiltonian(kx=kx, ky=ky-epsilon)
    dhdkx = ( hgridplusx -  hgridminusx )/(2*epsilon)
    dhdky = ( hgridplusy -  hgridminusy )/(2*epsilon)

    matrix_element_x = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex128)
    matrix_element_y = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex128)

    for i in range(Nk_in_path):
        for j in range(num_paths):
            buff = dhdkx[i,j,:,:] @ wf[i,j,:,:]
            matrix_element_x[i, j, :, :] = np.conjugate(wf[i, j, :, :].T) @ buff

            buff = dhdky[i,j,:,:] @ wf[i,j,:,:]
            matrix_element_y[i, j, :, :] = np.conjugate(wf[i, j, :, :].T) @ buff

    E_ort = np.array([E_dir[1], -E_dir[0]])

    mel_in_path = matrix_element_x[:, path_idx, :, :] * E_dir[0] + matrix_element_y[:, path_idx, :, :] * E_dir[1]
    mel_ortho = matrix_element_x[:, path_idx, :, :] * E_ort[0] + matrix_element_y[:, path_idx, :, :] * E_ort[1]

    return mel_in_path.reshape(Nk_in_path, n, n), mel_ortho.reshape(Nk_in_path, n, n)

def make_matrix_elements_dipoles(params, hamiltonian, paths, dipole_in_path, dipole_ortho, e_in_path, E_dir, path_idx):

    Nk_in_path = params.Nk1
    num_paths = params.Nk2
    n = params.n
    gidx = params.gidx
    epsilon = params.epsilon

    # derivative of band structure

    pathsplusx = np.copy(paths)
    pathsplusx[:, :, 0] += epsilon
    pathsminusx = np.copy(paths)
    pathsminusx[:, :, 0] -= epsilon
    pathsplusy = np.copy(paths)
    pathsplusy[:, :, 1] += epsilon
    pathsminusy = np.copy(paths)
    pathsminusy[:, :, 1] -= epsilon

    pathsplus2x = np.copy(paths)
    pathsplus2x[:, :, 0] += 2*epsilon
    pathsminus2x = np.copy(paths)
    pathsminus2x[:, :, 0] -= 2*epsilon
    pathsplus2y = np.copy(paths)
    pathsplus2y[:, :, 1] += 2*epsilon
    pathsminus2y = np.copy(paths)
    pathsminus2y[:, :, 1] -= 2*epsilon

    eplusx, wfplusx = diagonalize(params, hamiltonian, pathsplusx)
    eminusx, wfminusx = diagonalize(params, hamiltonian, pathsminusx)
    eplusy, wfplusy = diagonalize(params, hamiltonian, pathsplusy)
    eminusy, wfminusy = diagonalize(params, hamiltonian, pathsminusy)

    eplus2x, wfplus2x = diagonalize(params, hamiltonian, pathsplus2x)
    eminus2x, wfminus2x = diagonalize(params, hamiltonian, pathsminus2x)
    eplus2y, wfplus2y = diagonalize(params, hamiltonian, pathsplus2y)
    eminus2y, wfminus2y = diagonalize(params, hamiltonian, pathsminus2y)

    ederivx = ( - eplus2x + 8 * eplusx - 8 * eminusx + eminus2x)/(12*epsilon)
    ederivy = ( - eplus2y + 8 * eplusy - 8 * eminusy + eminus2y)/(12*epsilon)

    # In path direction and orthogonal

    E_ort = np.array([E_dir[1], -E_dir[0]])
    ederiv_in_path = E_dir[0] * ederivx + E_dir[1] * ederivy
    ederiv_ortho = E_ort[0] * ederivx + E_ort[1] * ederivy
    # matrix elements

    mel_in_path = np.zeros([Nk_in_path, n, n], dtype=np.complex128)
    mel_ortho = np.zeros([Nk_in_path, n, n], dtype=np.complex128)

    for i in range(n):
        mel_in_path[:, i, i] += ederiv_in_path[:, path_idx, i]
        mel_ortho[:, i, i] += ederiv_ortho[:, path_idx, i]
        for j in range(n):
            if i != j:
                mel_in_path[:, i, j] += 1j*dipole_in_path[:, i, j] * (e_in_path[:, j]-e_in_path[:, i])
                mel_ortho[:, i, j] += 1j*dipole_ortho[:, i, j] * (e_in_path[:, j]-e_in_path[:, i])

    return mel_in_path.reshape(Nk_in_path, n, n), mel_ortho.reshape(Nk_in_path, n, n)

def current_per_path(params, mel_in_path, mel_ortho, density_matrix):

    n = params.n
    Nt = params.Nt
    current_in_path = np.zeros(Nt, dtype=np.complex128)
    current_in_path_intraband = np.zeros(Nt, dtype=np.complex128)
    current_ortho = np.zeros(Nt, dtype=np.complex128)
    current_ortho_intraband = np.zeros(Nt, dtype=np.complex128)


    for i_t in range(Nt):
        for i in range(n):
            current_in_path[i_t] += - np.sum(mel_in_path[:, i, i] * density_matrix[:, i_t, i, i].real)
            current_in_path_intraband[i_t] += - np.sum(mel_in_path[:, i, i] * density_matrix[:, i_t, i, i].real)
            current_ortho[i_t] += - np.sum(mel_ortho[:, i, i] * density_matrix[:, i_t, i, i].real)
            current_ortho_intraband[i_t] += - np.sum(mel_ortho[:, i, i] * density_matrix[:, i_t, i, i].real)
            for j in range(n):
                if i != j:
                    current_in_path[i_t] += - np.sum(np.real(mel_in_path[:, i, j] * density_matrix[:,  i_t, j, i]))
                    current_ortho[i_t] += - np.sum(np.real(mel_ortho[:, i, j] * density_matrix[:,  i_t, j, i]))

    return current_in_path, current_in_path_intraband, current_ortho, current_ortho_intraband
