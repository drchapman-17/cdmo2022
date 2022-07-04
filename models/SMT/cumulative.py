from z3 import *
#
# Decompositon of cumulative.
#
# Inspired by the MiniZinc implementation:
# http://www.g12.csse.unimelb.edu.au/wiki/doku.php?id=g12:zinc:lib:minizinc:std:cumulative.mzn&s[]=cumulative
# The MiniZinc decomposition is discussed in the paper:
# A. Schutt, T. Feydy, P.J. Stuckey, and M. G. Wallace.
# 'Why cumulative decomposition is not as bad as it sounds.'
# Download:
# http://www.cs.mu.oz.au/%7Epjs/rcpsp/papers/cp09-cu.pdf
# http://www.cs.mu.oz.au/%7Epjs/rcpsp/cumu_lazyfd.pdf
#
#
# Parameters:
#
# s: start_times    assumption: array of IntVar -> X
# d: durations      assumption: array of int -> Block width
# r: resources      assumption: array of int -> Block height
# b: resource limit assumption: IntVar or int -> d
#
# Note: since I don't know how to extract the bounds of the
#       domains, both times_min and times_max1 are required
#       which is the lower/upper limits of s (the start_times).
#       Which makes it slower...
#
def cumulative(sol, s, d, r, b,times_min,times_max1):

  tasks = [i for i in range(len(s)) if r[i] > 0 and d[i] > 0]
  
  # how do I get the upper/lower value of a decision variable?
  # times_min = min([s[i].Min() for i in tasks])
  # times_max = max([s[i].Max() + max(d) for i in tasks])
  times_max = times_max1 + max(d)
  for t in range(times_min, times_max + 1):
    for i in tasks:
      sol.add(Sum([(If(s[i] <= t,1,0) * If(t < s[i] + d[i],1,0))*r[i] for i in tasks])  <= b)

  # Somewhat experimental:
  # This constraint is needed to contrain the upper limit of b.
  if not isinstance(b, int):
    sol.add(b <= sum(r))