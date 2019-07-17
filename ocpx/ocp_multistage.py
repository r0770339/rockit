from .stage import Stage

class OcpMultiStage:
  def __init__(self):
    self.stages = []
    # Flag to make solve() faster when solving a second time (e.g. with different parameter values)
    self.is_transcribed = False

  def stage(self,**kwargs):
    s = Stage(self,**kwargs)
    self.stages.append(s)
    return s

  def method(self,method):
    self._method = method

  def solve(self):
    opti = self._method.opti
    if not self.is_transcribed:
      for s in self.stages:
        s._method.transcribe(s, opti)
      self.is_transcribed = True
    sol = opti.solve()