import numpy as np
from scipy import sparse

def ybus(buses, lines):
    nbus = len(buses)
    nline = len(lines)
    busset = np.arange(0, nbus)
    lineset = np.arange(0, nline)
    # buses
    # Bus(bindex=1.0, btype=3.0, Pd=0.0, Qd=0.0, Gs=0.0, Bs=0.0, area=1.0, Vm=1.06, Va=0.0, baseKV=132.0, bzone=1.0, Vmax=1.06, Vmin=0.94, inline=[], outline=[0, 1])
    # lines
    # Line(lindex=1, fbus=0, tbus=1, r=0.02, x=0.06, b=0.03, u=1.3, shft=0.0, tap=0.0, angmin=-6.283185307179586, angmax=6.283185307179586)
    #
    #````````````````````````````````````````````````````````````````````````
    # f: from
    # t: to
    Ybus = np.zeros( [ nbus, nbus ], dtype=complex ) # n x n matrix 만들어줌.
    yff = np.zeros( [ nline, 1], dtype=complex )
    yft = np.zeros( [ nline, 1], dtype=complex )
    ytf = np.zeros( [ nline, 1], dtype=complex )
    ytt = np.zeros( [ nline, 1], dtype=complex )
    tau = np.zeros( [ nline, 1], dtype=complex )

    for l in lineset:
        
        tau[l] = np.exp(+ 1j * lines[l].shft) if lines[l].tap == 0 else lines[l].tap * np.exp(+ 1j * lines[l].shft)

        ytt[l] = 1/(lines[l].r + 1j * lines[l].x) + 1j * lines[l].b / 2
        yff[l] = (1/(lines[l].r + 1j * lines[l].x) + 1j * lines[l].b / 2) / (tau[l] * np.conj(tau[l]))
        yft[l] = - (1/(lines[l].r + 1j * lines[l].x)) / np.conj(tau[l])
        ytf[l] = - (1/(lines[l].r + 1j * lines[l].x)) / tau[l]

        Ybus[lines[l].fbus, lines[l].tbus] = yft[l]
        Ybus[lines[l].tbus, lines[l].fbus] = ytf[l]
        Ybus[lines[l].fbus, lines[l].fbus] += yff[l]
        Ybus[lines[l].tbus, lines[l].tbus] += ytt[l]
    
    for b in busset:
        Ybus[b, b] += buses[b].Gs + 1j * buses[b].Bs
    

    return Ybus, yff, yft, ytf, ytt