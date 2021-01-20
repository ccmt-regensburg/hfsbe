import numpy as np
###############################################################################
# K-Point meshes
###############################################################################
def rect_mesh(params, E_dir, type_real_np):
    '''
    Create a rectangular mesh
    '''
    # Number of kpoints in each of the two paths
    Nk_in_path_integer = params.Nk1
    Nk_in_path         = type_real_np(Nk_in_path_integer)
    # relative distance (in units of 2pi/a) of both paths to Gamma
    rel_dist_to_Gamma = type_real_np(params.rel_dist_to_Gamma)
    a                 = type_real_np(params.a)
    length_path_in_BZ = type_real_np(params.length_path_in_BZ)
    num_paths         = params.Nk2

    alpha_array = np.linspace(-0.5 + (1/(2*Nk_in_path)),
                              0.5 - (1/(2*Nk_in_path)), num=Nk_in_path_integer)
    vec_k_path = E_dir*length_path_in_BZ

    vec_k_ortho = 2.0*(np.pi/a)*rel_dist_to_Gamma*np.array([E_dir[1], -E_dir[0]])

    # Containers for the mesh, and BZ directional paths
    mesh = []
    paths = []

    # Create the kpoint mesh and the paths
    for path_index in np.linspace(-num_paths + 1, num_paths - 1, num=num_paths):
        # Container for a single path
        path = []
        for alpha in alpha_array:
            # Create a k-point
            kpoint = path_index*vec_k_ortho + alpha*vec_k_path

            mesh.append(kpoint)
            path.append(kpoint)

        # Append the a1'th path to the paths array
        paths.append(path)

    dk = length_path_in_BZ/Nk_in_path
    kweight = 2*rel_dist_to_Gamma*length_path_in_BZ/(Nk_in_path - 1)
    return dk, kweight, np.array(mesh), np.array(paths)


def hex_mesh(P):
    '''
    Create a hexagonal mesh
    '''
    def is_in_hex(p):
        # Returns true if the point is in the hexagonal BZ.
        # Checks if the absolute values of x and y components of p are within
        # the first quadrant of the hexagon.
        x = np.abs(p[0])
        y = np.abs(p[1])
        return ((y <= 2.0*np.pi/(np.sqrt(3)*P.a)) and
                (np.sqrt(3.0)*x + y <= 4*np.pi/(np.sqrt(3)*P.a)))

    def reflect_point(p):
        x = p[0]
        y = p[1]
        if y > 2*np.pi/(np.sqrt(3)*P.a):
            # Crosses top
            p -= P.b2
        elif y < -2*np.pi/(np.sqrt(3)*P.a):
            # Crosses bottom
            p += P.b2
        elif np.sqrt(3)*x + y > 4*np.pi/(np.sqrt(3)*P.a):
            # Crosses top-right
            p -= P.b1 + P.b2
        elif -np.sqrt(3)*x + y < -4*np.pi/(np.sqrt(3)*P.a):
            # Crosses bot-right
            p -= P.b1
        elif np.sqrt(3)*x + y < -4*np.pi/(np.sqrt(3)*P.a):
            # Crosses bot-left
            p += P.b1 + P.b2
        elif -np.sqrt(3)*x + y > 4*np.pi/(np.sqrt(3)*P.a):
            # Crosses top-left
            p += P.b1
        return p

    # Containers for the mesh, and BZ directional paths
    mesh = []
    paths = []

    # Create the Monkhorst-Pack mesh
    if P.align == 'M':
        if P.Nk2%3 != 0:
            raise RuntimeError("Nk2: " + "{:d}".format(P.Nk2) +
                               " needs to be divisible by 3")
        b_a2 = (2*np.pi/(3*P.a))*np.array([1, np.sqrt(3)])
        alpha1 = np.linspace(-0.5 + (1/(2*P.Nk1)), 0.5 - (1/(2*P.Nk1)), num=P.Nk1)
        alpha2 = np.linspace(-1.0 + (1.5/(2*P.Nk2)), 0.5 - (1.5/(2*P.Nk2)), num=P.Nk2)
        for a2 in alpha2:
            # Container for a single gamma-M path
            path_M = []
            for a1 in alpha1:
                # Create a k-point
                kpoint = a1*P.b1 + a2*b_a2
                # If current point is in BZ, append it to the mesh and path_M
                if is_in_hex(kpoint):
                    mesh.append(kpoint)
                    path_M.append(kpoint)
                # If current point is NOT in BZ, reflect it along
                # the appropriate axis to get it in the BZ, then append.
                else:
                    while not is_in_hex(kpoint):
                        kpoint = reflect_point(kpoint)
                    mesh.append(kpoint)
                    path_M.append(kpoint)
            # Append the a1'th path to the paths array
            paths.append(path_M)

    elif P.align == 'K':
        if P.Nk1%3 != 0 or P.Nk1%2 != 0:
            raise RuntimeError("Nk1: " + "{:d}".format(P.Nk1) +
                               " needs to be divisible by 3 and even")
        if P.Nk2%3 != 0:
            raise RuntimeError("Nk2: " + "{:d}".format(P.Nk2) +
                               " needs to be divisible by 3")
        b_a1 = 8*np.pi/(P.a*3)*np.array([1, 0])
        b_a2 = 4*np.pi/(P.a*3)*np.array([0, np.sqrt(3)])
        # Extend over half of the b2 direction and 1.5x the b1 direction
        # (extending into the 2nd BZ to get correct boundary conditions)
        alpha1 = np.linspace(-0.5 + (1.5/(2*P.Nk1)), 1.0 - (1.5/(2*P.Nk1)), P.Nk1)
        alpha2 = np.linspace(0 + (0.5/(2*P.Nk2)), 0.5 - (0.5/(2*P.Nk2)), P.Nk2)
        for a2 in alpha2:
            path_K = []
            for a1 in alpha1:
                kpoint = a1*b_a1 + a2*b_a2
                if is_in_hex(kpoint):
                    mesh.append(kpoint)
                    path_K.append(kpoint)
                else:
                    while not is_in_hex(kpoint):
                        kpoint = reflect_point(kpoint)
                    # kpoint -= (2*np.pi/a) * np.array([1, 1/np.sqrt(3)])
                    mesh.append(kpoint)
                    path_K.append(kpoint)
            paths.append(path_K)

    return np.array(mesh), np.array(paths), (3*np.sqrt(3)/2)*(4*np.pi/(P.a*3))**2
