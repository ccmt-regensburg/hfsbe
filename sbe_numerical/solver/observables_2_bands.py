import numpy as np
from sbe.utility import conversion_factors as co
from dipole_numerical import hamiltonian, diagonalize, derivative, dipole_elements

def hderiv(Nk_in_path, num_paths, n, paths, epsilon):

    hgridplusx = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex)
    hgridminusx = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex)
    hgridplusy = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex)
    hgridminusy = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex)

    dhdkx = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex)
    dhdky = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex)

    for i in range(Nk_in_path):
        for j in range(num_paths):
            kx = paths[j, i, 0]
            ky = paths[j, i, 1]
            hgridplusx[i, j, :, :] = hamiltonian(kx + epsilon, ky)
            hgridminusx[i, j, :, :] = hamiltonian(kx - epsilon, ky)
            hgridplusy[i, j, :, :] = hamiltonian(kx, ky + epsilon)
            hgridminusy[i, j, :, :] = hamiltonian(kx, ky - epsilon)

    dhdkx = (hgridplusx - hgridminusx)/(2*epsilon)
    dhdky = (hgridplusy - hgridminusy)/(2*epsilon)

    return dhdkx, dhdky

def matrix_elements(Nk_in_path, num_paths, n, paths, gidx, epsilon):

    e, wf = diagonalize(Nk_in_path, num_paths, n, paths, gidx)
    dhdkx, dhdky = hderiv(Nk_in_path, num_paths, n, paths, epsilon)

    matrix_element_x = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex)
    matrix_element_y = np.empty([Nk_in_path, num_paths, n, n], dtype=np.complex)

    for i in range(Nk_in_path):
        for j in range(num_paths):
            matrix_element_x[i, j, :, :] = - np.conjugate(wf[i, j, :, :].T).dot(np.dot(dhdkx[i, j, :, :], wf[i, j, :, :]))
            matrix_element_y[i, j, :, :] = - np.conjugate(wf[i, j, :, :].T).dot(np.dot(dhdky[i, j, :, :], wf[i, j, :, :]))

    return matrix_element_x, matrix_element_y

def current_in_path(Nk_in_path, num_paths, Nt, density_matrix, n, paths, gidx, epsilon, path_idx):

    current_in_path = np.zeros([Nt, 2], dtype=np.float64)

    matrix_element_x, matrix_element_y = matrix_elements(Nk_in_path, num_paths, n, paths, gidx, epsilon)

    for i_t in range(Nt):
        for i_k in range(Nk_in_path):     #length gauge only!
            current_in_path[i_t, 0] +=  matrix_element_x[i_k, path_idx, 0, 0].real * density_matrix[i_k, path_idx, i_t, 0].real
            current_in_path[i_t, 0] +=  matrix_element_x[i_k, path_idx, 1, 1].real * density_matrix[i_k, path_idx, i_t, 3].real
            current_in_path[i_t, 0] +=  2*np.real(matrix_element_x[i_k, path_idx, 0, 1] * density_matrix[i_k, path_idx, i_t, 2])
            
            current_in_path[i_t, 1] +=  matrix_element_y[i_k, path_idx, 0, 0].real * density_matrix[i_k, path_idx, i_t, 0].real
            current_in_path[i_t, 1] +=  matrix_element_y[i_k, path_idx, 1, 1].real * density_matrix[i_k, path_idx, i_t, 3].real
            current_in_path[i_t, 0] +=  2*np.real(matrix_element_y[i_k, path_idx, 0, 1] * density_matrix[i_k, path_idx, i_t, 2])         
    return current_in_path
