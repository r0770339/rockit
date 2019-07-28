# robust optimal control
from ocpx import *
from casadi import sumsqr, vertcat, sin, cos, vec, diag, horzcat, sqrt
import matplotlib.pyplot as plt
import numpy as np


ocp = Ocp()

template = Stage(T=1)
x1 = template.state()
x2 = template.state()

x = vertcat(x1, x2)
u = template.state()

delta = template.parameter()

template.set_der(x1, x2)
template.set_der(x2, -0.1*(1-x1**2 + delta)*x2 - x1 + u + delta)

template.set_der(u, 0)

template.subject_to(u <= 40)
template.subject_to(u >= -40)
template.subject_to(x1 >= -0.25)
L = template.variable()
template.add_objective(L)
template.subject_to(L>= sumsqr(x1-3))
bound = lambda t: 2 + 0.1*cos(10*t)
template.subject_to(x1 <= bound(template.t))
template.method(MultipleShooting(N=20, M=1, intg='rk'))

def recurse(parent_stage, branching_var, branchings, current_depth=0):
  if len(branchings)==0: return

  non_anticipatory = []
  for b in branchings[0]:
    stage = parent_stage.stage(template, t0=current_depth)
    stage.set_value(branching_var, b)
    recurse(stage, branching_var, branchings[1:], current_depth+1)

    if current_depth==0:
      stage.master.subject_to(stage.at_t0(x)==(1.0,0))
    else:
      stage.master.subject_to(stage.at_t0(x)==parent_stage.at_tf(x))
    
    non_anticipatory.append(stage.at_t0(u))
  for uk, ukp in zip(non_anticipatory[1:],non_anticipatory[:-1]):
    stage.master.subject_to(uk==ukp)



branchings = [[-1,1]]*3
recurse(ocp, delta, branchings)

ocp.solver('ipopt',{"expand":True})

sol = ocp.solve()


plt.figure()
for s in ocp.iter_stages():
  ts, xsol = sol.sample(s, x1, grid='integrator')
  plt.plot(ts, xsol, '-o')

  plt.plot(ts, bound(ts),'r-')

plt.xlabel('Time [s]')
plt.ylabel('x1')

plt.show()
