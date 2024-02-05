import numpy as np
from math import radians
from scipy.io import loadmat # .mat 파일 불러오는 방법
from struct_network import Bus, Line, Generator

def readnetwork(testsystem):

    filename_mat = f'D:/Github/Optimization/data/network/mat/{testsystem}.mat'
    mpc = loadmat(filename_mat)['mpc'] # mpc는 MATPOWER 

    linedata = mpc['branch'][0,0] # array로 여러 번 감싸져 있어서 [0][0]으로 제거
    busdata = mpc['bus'][0,0]
    gendata = mpc['gen'][0,0]
    gcostdata = mpc['gencost'][0,0]
    baseMVA = mpc['baseMVA'][0,0][0,0]

    nbus = busdata.shape[0]
    nline = linedata.shape[0]
    ngen = gendata.shape[0]

    datamat = mpc

    #===========================================================================================================
    buses = []
    for i in np.arange(0, nbus):
        bindex = busdata[i, 0]
        btype = busdata[i, 1] # BUS TYPE 2 bus type (1 = PQ, 2 = PV, 3 = ref, 4 = isolated)
        Pd = busdata[i, 2] / baseMVA
        Qd = busdata[i, 3] / baseMVA
        Gs = busdata[i, 4] / baseMVA # shunt conductance
        Bs = busdata[i, 5] / baseMVA # shunt susceptance
        area = busdata[i, 6]
        Vm = busdata[i, 7]
        Va = radians(busdata[i, 8])
        baseKV = busdata[i, 9]
        bzone = busdata[i, 10]
        Vmax = busdata[i, 11]
        Vmin = busdata[i, 12]
        b = Bus(bindex, btype, Pd, Qd, Gs, Bs, area, Vm, Va, baseKV, bzone, Vmax, Vmin)
        # 출력하면...
        # Bus(bindex=1.0, btype=3.0, Pd=0.0, Qd=0.0, Gs=0.0, Bs=0.0, area=1.0, Vm=1.06, Va=0.0, baseKV=132.0, bzone=1.0, Vmax=1.06, Vmin=0.94, inline=[], outline=[])
        buses.append(b)

    bidxmap = {buses[i].bindex: i for i in np.arange(0, nbus)}

    #============================================================================================================
    lines = []
    for i in np.arange(0, nline):
        lindex = i+1
        fbus = bidxmap[ int(linedata[i, 0]) ]
        tbus = bidxmap[ int(linedata[i, 1]) ]
        r = linedata[i, 2]  # resistance
        x = linedata[i, 3]  # reactance
        b = linedata[i, 4]  # total line charging susceptance
        u = linedata[i, 5]/baseMVA
        tap = linedata[i, 8]
        shft = radians(linedata[i, 9])
        angmin = radians(linedata[i, 11])  # minimum angle difference
        angmax = radians(linedata[i, 12])  # maximum angle difference
        buses[tbus].inline.append(i)
        buses[fbus].outline.append(i)
        l = Line(lindex, fbus, tbus, r, x, b, u, shft, tap, angmin, angmax)
        lines.append(l)

    #============================================================================================================
    generators = []
    for i in np.arange(0, ngen):
        gindex = i+1
        gtype = "NotDefined"
        location = bidxmap[gendata[i, 1-1]]
        Pg = gendata[i, 2-1]/baseMVA
        Qg = gendata[i, 3-1]/baseMVA
        Qmax = gendata[i, 4-1]/baseMVA
        Qmin = gendata[i, 5-1]/baseMVA
        Vg = gendata[i, 6-1]
        mBase = gendata[i, 7-1]
        status = gendata[i, 8-1]
        Pmax = gendata[i, 9-1]/baseMVA
        Pmin = gendata[i, 10-1]/baseMVA
        if len(gcostdata[i, 5-1:]) == 3:
            cost = [gcostdata[i, 5-1], gcostdata[i, 6-1], gcostdata[i, 7-1]]
        elif len(gcostdata[i, 5-1:]) == 2:
            cost = [0, gcostdata[i, 5-1], gcostdata[i, 6-1]]
        else:
            print("generator cost format is incompatible")

        SUcost = gcostdata[i, 2-1]
        SDcost = gcostdata[i, 3-1]
        RU = 0
        RD = 0
        UPtime = 0
        DNtime = 0
        g = Generator(gindex, gtype, location, Pg, Qg, Qmax, Qmin, Vg, mBase,
                    status, Pmax, Pmin, cost, SUcost, SDcost, RU, RD, UPtime, DNtime)
        generators.append(g)

    return buses, lines, generators, datamat