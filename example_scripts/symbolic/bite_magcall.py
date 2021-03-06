import numpy as np
import matplotlib.pyplot as plt
import sympy as sp

from sbe.example import BiTeResummed
from sbe.dipole import SymbolicDipole, SymbolicParameterDipole, \
                         SymbolicCurvature
from sbe.utility import evaluate_njit_matrix as evmat

np.set_printoptions(linewidth=200)

eV_conv = 0.03674932176
au_conv = (1/eV_conv)


a = 8.28834
C0 = -0.00647156
A = 0.0422927
c2 = 0.0117598
r = 0.109031
ksym = 0.0635012
kasym = 0.113773


def bite_resummed_num(kx, ky):
    mb = 0.0003
    bite = BiTeResummed(C0=C0, c2=c2, A=A, r=r, ksym=ksym, kasym=kasym)
    h_sym, e_sym, wf_sym, ediff_sym = bite.eigensystem(gidx=1)
    # test = sp.lambdify(ediff_sym[1].free_symbols, ediff_sym[1], "numpy")
    # print(test(kx=kx, ky=ky, mb=mb))

    print("Hamiltonian")
    print(evmat(bite.hfjit, kx=kx, ky=ky, mb=mb))
    print("Hamiltonian d/dkx")
    print(evmat(bite.hderivfjit[0], kx=kx, ky=ky, mb=mb))
    print("Hamiltonian d/dky")
    print(evmat(bite.hderivfjit[1], kx=kx, ky=ky, mb=mb))

    print("Valence Band")
    print(bite.efjit[0](kx=kx, ky=ky, mb=mb))
    print("Conduction Band")
    print(bite.efjit[1](kx=kx, ky=ky, mb=mb))

    print("Valence band d/dkx")
    print(bite.ederivfjit[0](kx=kx, ky=ky, mb=mb))
    print("Valence band d/dky")
    print(bite.ederivfjit[1](kx=kx, ky=ky, mb=mb))
    print("Conduction band d/dkx")
    print(bite.ederivfjit[2](kx=kx, ky=ky, mb=mb))
    print("Conduction band d/dky")
    print(bite.ederivfjit[3](kx=kx, ky=ky, mb=mb))

    print("Valence & Conduction band wave function")
    print(evmat(bite.Ujit, kx=kx, ky=ky, mb=mb))

    dip = SymbolicDipole(h_sym, e_sym, wf_sym, offdiagonal_k=True)
    print("Dipole Matrix x-Component")
    print(evmat(dip.Axfjit, kx=kx, ky=ky, mb=mb))
    print("Dipole Matrix y-Component")
    print(evmat(dip.Ayfjit, kx=kx, ky=ky, mb=mb))

    print("Dipole Matrix x-Component (k neq kp)")
    print(evmat(dip.Axfjit_offk, kx=kx, ky=ky, kxp=kx, kyp=ky, mb=mb))
    print("Dipole Matrix y-Component (k neq kp)")
    print(evmat(dip.Ayfjit_offk, kx=kx, ky=ky, kxp=kx, kyp=ky, mb=mb))

    mb_sym = sp.Symbol('mb', real=True)
    dip_mb = SymbolicParameterDipole(h_sym, wf_sym, mb_sym)
    print("Dipole Matrix mb-Component")
    print(evmat(dip_mb.Apfjit, kx=kx, ky=ky, mb=mb))

    cur = SymbolicCurvature(h_sym, dip.Ax, dip.Ay)
    print("Berry curvature")
    print(evmat(cur.Bfjit, kx=kx, ky=ky, mb=mb))


if __name__ == "__main__":
    N = 10
    kinit = np.linspace(-np.pi/a, np.pi/a, N)
    kx = kinit
    ky = np.zeros(N)
    bite_resummed_num(kx, ky)
