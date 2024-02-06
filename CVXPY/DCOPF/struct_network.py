from dataclasses import dataclass, field
from typing import List


# 그냥 클래스 만든 거임.
# 근데 dataclass라는 특수한 형태로 만들고 
# 전부 다 묶어서 사용할 때는 attribute 불러오는 방식으로 사용.
@dataclass
class Bus:
   bindex: int
   btype: int
   Pd: float
   Qd: float
   Gs: float
   Bs: float
   area: int
   Vm: float
   Va: float
   baseKV: float
   bzone: int
   Vmax: float
   Vmin: float
   inline: List[int] = field(default_factory=list, init=False)
   outline: List[int] = field(default_factory=list, init=False)

@dataclass
class Line:
   lindex: int
   fbus: int  # the "from" node
   tbus: int  # the "to" node
   r: float  # the resistance value
   x: float  # the reactance value
   b: float  # the susceptance value
   u: float  # the capacity of the line
   shft: float  # transformer phase shift (degress)
   tap: float
   angmin: float
   angmax: float

@dataclass
class Generator:
   gindex: int
   gtype: str
   location: int
   Pg: float
   Qg: float
   Qmax: float
   Qmin: float
   Vg: float
   mBase: float
   status: int
   Pmax: float
   Pmin: float
   cost: List[float]
   SUcost: float
   SDcost: float
   RU: float
   RD: float
   UPtime: float
   DNtime: float