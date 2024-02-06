import numpy as np
from math import radians
from scipy.io import loadmat # .mat 파일 불러오는 방법
from struct_network import Bus, Line, Generator

def readnetwork(testsystem):

    filename_mat = f'D:/Github/Optimization/data/network/mat/{testsystem}.mat'
    mpc = loadmat(filename_mat)['mpc'] # mpc는 MATPOWER Case의 줄임말.

    linedata = mpc['branch'][0,0] # array로 여러 번 감싸져 있어서 [0][0]으로 제거
    busdata = mpc['bus'][0,0]
    gendata = mpc['gen'][0,0]
    gcostdata = mpc['gencost'][0,0]
    baseMVA = mpc['baseMVA'][0,0][0,0]

    nbus = busdata.shape[0]   # 버스 개수
    nline = linedata.shape[0] # 선로 개수
    ngen = gendata.shape[0]   # 발전기 개수

    datamat = mpc

    #===========================================================================================================
    # IEEE 30의 경우 1번만 ref.로 되어 있고, 나머지는 모두 PQ로 되어 있음.
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
        # Bus는 어떤 class로 정의되어 있음.
        # Bus에 인덱스로 불러온 것들 다 넣어서 b라고 객체화.
        b = Bus(bindex, btype, Pd, Qd, Gs, Bs, area, Vm, Va, baseKV, bzone, Vmax, Vmin)
        # 출력하면...
        # Bus(bindex=1.0, btype=3.0, Pd=0.0, Qd=0.0, Gs=0.0, Bs=0.0, area=1.0, Vm=1.06, Va=0.0, baseKV=132.0, bzone=1.0, Vmax=1.06, Vmin=0.94, inline=[], outline=[])
        # 이렇게 만들면, Bus.Pd 이런 식으로 불러오기 편함(사실 클래스 만들고 attrubute 불러오는 거임.).
        buses.append(b)

    bidxmap = {buses[i].bindex: i for i in np.arange(0, nbus)}
    # bidxmap: {1.0: 0, 2.0: 1, 3.0: 2, 4.0: 3, 5.0: 4, 6.0: 5, 7.0: 6, ....
    #============================================================================================================
    # Python에서는 0부터 다루지만 bus index는 1부터 시작함.
    lines = []
    for i in np.arange(0, nline):
        lindex = i+1
        fbus = bidxmap[ int(linedata[i, 0]) ] # e.g. bus1 --> 0    buses 인덱싱할 때 0부터 해야 맞음.
        tbus = bidxmap[ int(linedata[i, 1]) ] # e.g. bus2 --> 1
        r = linedata[i, 2]  # resistance
        x = linedata[i, 3]  # reactance
        b = linedata[i, 4]  # total line charging susceptance
        u = linedata[i, 5]/baseMVA # Rate_A: branch flow limit(manual 63쪽에 설명 나옴.)
        tap = linedata[i, 8] # 원본 데이터에는 ratio라고 되어 있음.
        shft = radians(linedata[i, 9]) # 원본 데이터에는 angle이라고 되어 있음.
        angmin = radians(linedata[i, 11])  # minimum angle difference
        angmax = radians(linedata[i, 12])  # maximum angle difference
        buses[tbus].inline.append(i)  # i번째 line은 tbus에 도착.
        buses[fbus].outline.append(i) # i번째 line은 fbus에서 출발.
        l = Line(lindex, fbus, tbus, r, x, b, u, shft, tap, angmin, angmax)
        # 아래와 같이 생겼음.
        # Line(lindex=1, fbus=0, tbus=1, r=0.02, x=0.06, b=0.03, u=1.3, shft=0.0, tap=0.0, angmin=-6.283185307179586, angmax=6.283185307179586)
        lines.append(l)

    #============================================================================================================
    generators = []
    for i in np.arange(0, ngen):
        gindex = i+1
        gtype = "NotDefined"
        location = bidxmap[gendata[i, 0]]
        Pg = gendata[i, 1]/baseMVA
        Qg = gendata[i, 2]/baseMVA
        Qmax = gendata[i, 3]/baseMVA
        Qmin = gendata[i, 4]/baseMVA
        Vg = gendata[i, 5]
        mBase = gendata[i, 6]
        status = gendata[i, 7]
        Pmax = gendata[i, 8]/baseMVA
        Pmin = gendata[i, 9]/baseMVA
        # 발전 비용 함수 정리.
        # 값이 두 개인 경우가 있고 하나인 경우가 있음.
        if len(gcostdata[i, 4:]) == 3:
            cost = [gcostdata[i, 4], gcostdata[i, 5], gcostdata[i, 6]]
        elif len(gcostdata[i, 4:]) == 2:
            cost = [0, gcostdata[i, 4], gcostdata[i, 5]]
        else:
            print("generator cost format is incompatible")

        SUcost = gcostdata[i, 1] # startup
        SDcost = gcostdata[i, 2] # shutdown
        RU = 0
        RD = 0
        UPtime = 0
        DNtime = 0
        g = Generator(gindex, gtype, location, Pg, Qg, Qmax, Qmin, Vg, mBase,
                    status, Pmax, Pmin, cost, SUcost, SDcost, RU, RD, UPtime, DNtime)
        generators.append(g)

    return buses, lines, generators, datamat