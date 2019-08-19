# OCPx
[![pipeline status](https://gitlab.mech.kuleuven.be/meco-software/ocpx/badges/master/pipeline.svg)](https://gitlab.mech.kuleuven.be/meco-software/ocpx/commits/master)
[![coverage report](https://gitlab.mech.kuleuven.be/meco-software/ocpx/badges/master/coverage.svg)](https://meco-software.pages.mech.kuleuven.be/ocpx/coverage/index.html)
[![html docs](https://img.shields.io/static/v1.svg?label=docs&message=online&color=informational)](http://meco-software.pages.mech.kuleuven.be/ocpx)
[![pdf docs](https://img.shields.io/static/v1.svg?label=docs&message=pdf&color=red)](http://meco-software.pages.mech.kuleuven.be/ocpx/documentation-ocpx.pdf)

# Description

Rockit (Rapid Optimal Control kit) is a software framework to quickly prototype optimal control problems (aka dynamic optimization) that may arise in engineering:
iterative learning (ILC), model predictive control (NMPC), motion planning.

Notably, the software allows free end-time problems and multi-stage optimal problems.
The software is currently focused on direct methods and relieas eavily on [CasADi](http://casadi.org).

# Installation
Install using pip: `pip install rockit`

# Hello world
(Taken from the [example directory](https://gitlab.mech.kuleuven.be/meco-software/rockit/blob/master/examples/hello_world.py))
Some recommendations for a productive setup:

Import the project:
```python
from ocpx import *
```

Start an optimal control environment with a time horizon of 10 seconds (free time problems can be configured with `FreeTime(initial_guess)`).
```python
ocp = Ocp(T=10)
```

Define two scalar states (vectors and matrices also supported):
```python
x1 = ocp.state()
x2 = ocp.state()
```

Define one control input:
```python
u = ocp.control(order=0)
```

Specify ODE (DAEs also supported with `ocp.algebraic` and `add_alg`):
```python
ocp.set_der(x1, (1 - x2**2) * x1 - x2 + u)
ocp.set_der(x2, x1)
```

Lagrange objective:
```python
ocp.add_objective(ocp.integral(x1**2 + x2**2 + u**2))
```

Path constraints:
```python
ocp.subject_to(      u <= 1)
ocp.subject_to(-1 <= u     )
ocp.subject_to(x1 >= -0.25)
```

Initial constraints:
```python
ocp.subject_to(ocp.at_t0(x1) == 0)
ocp.subject_to(ocp.at_t0(x2) == 1)
```

Pick an NLP solver backend (CasADi `nlpsol` plugin):
```python
ocp.solver('ipopt')
```

Pick a solution method:
```python
method = MultipleShooting(N=10, M=1, intg='rk')
#method = DirectCollocation(N=20)
ocp.method(method)
```

Solve:
```python
sol = ocp.solve()
```

Show structure:
```python
ocp.spy()
```

Post-processing:
```
tsa, x1a = sol.sample(x1, grid='control')
tsa, x2a = sol.sample(x2, grid='control')

tsb, x1b = sol.sample(x1, grid='integrator')
tsb, x2b = sol.sample(x2, grid='integrator')


from pylab import *

figure(figsize=(10, 4))
subplot(1, 2, 1)
plot(tsb, x1b, '.-')
plot(tsa, x1a, 'o')
xlabel("Times [s]", fontsize=14)
grid(True)
title('State x1')

subplot(1, 2, 2)
plot(tsb, x2b, '.-')
plot(tsa, x2a, 'o')
legend(['grid_integrator', 'grid_control'])
xlabel("Times [s]", fontsize=14)
title('State x2')
grid(True)

tsol, usol = sol.sample(u, grid='integrator',refine=100)

figure()
plot(tsol,usol)
title("Control signal")
xlabel("Times [s]")
grid(True)

tsc, x1c = sol.sample(x1, grid='integrator', refine=100)

figure(figsize=(15, 4))
plot(tsc, x1c, '-')
plot(tsa, x1a, 'o')
plot(tsb, x1b, '.')
xlabel("Times [s]")
grid(True)
```