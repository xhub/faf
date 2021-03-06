import siconos.numerics as N
import h5py
import numpy as np
from faf_tools import *
from faf_papi import *

class SiconosSolver():
    _name = None
    _gnuplot_name = None
    _API = None
    _TAG = None
    _iparam_iter = None
    _dparam_err = None
    _SO = None

    def _get(self, tab, index):
        if index is not None:
            return tab[index]
        else:
            return None

    def __init__(self, name=None, gnuplot_name=None, API=None, TAG=None, iparam_iter=None,
                 dparam_err=None, maxiter=None, precision=None, with_guess=None):
        self._name = name
        if (gnuplot_name==None):
            self._gnuplot_name = self._name
        else:
            self._gnuplot_name = gnuplot_name
        self._API = API
        self._TAG = TAG
        self._iparam_iter = iparam_iter
        self._dparam_err = dparam_err
        self._SO = N.SolverOptions(TAG)  # set default solver options
        if (maxiter==None):
            raise RuntimeError ("SiconosSolver() maxiter have to specified.")
        else :
            self._SO.iparam[0] = maxiter
        if (precision==None):
            raise RuntimeError ("SiconosSolver() precision have to specified.")
        else:
            self._SO.dparam[0] = precision
        if (with_guess==None):
            raise RuntimeError ("SiconosSolver() with_guess have to specified.")
        else:
            self._with_guess = with_guess


    def SolverOptions(self):
        return self._SO

    def __call__(self, problem, reactions, velocities):
        real_time = c_float()
        proc_time = c_float()
        flpops = c_longlong()
        mflops = c_float()
        init_flop()
        info = self._API(problem, reactions, velocities, self._SO)

        get_flop(real_time, proc_time, flpops, mflops)
        return (info, self._get(self._SO.iparam, self._iparam_iter),
                self._get(self._SO.dparam, self._dparam_err),
                real_time.value, proc_time.value,
                flpops.value, mflops.value)

    def guess(self, filename):
        problem = read_fclib_format(filename)[1]

        with h5py.File(filename, 'r') as f:
            psize = numberOfDegreeofFreedomContacts(filename)
            if self._with_guess and 'guesses' in f:
                number_of_guesses = f['guesses']['number_of_guesses'][0]
                velocities = f['guesses']['1']['u'][:]
                reactions = f['guesses']['1']['r'][:]
            else:
                # guess is missing
                reactions = np.zeros(psize)
                velocities = np.zeros(psize)

        return reactions, velocities

    def name(self):
        return self._name
    def gnuplot_name(self):
        return self._gnuplot_name

class BogusSolver(SiconosSolver):
    def read_fclib_format(self, filename):
        return BogusInterface.FCLib.fclib_read_local(filename)

def wrap_bogus_solve(problem, reactions, velocities, SO):
    res = BogusInterface.solve_fclib(problem, reactions, velocities, SO)
    return res




class SiconosHybridSolver(SiconosSolver):

    def guess(self, filename):
        pfilename = os.path.splitext(filename)[0]
        with h5py.File('comp.hdf5', 'r') as comp_file:
            return extern_guess(pfilename, 'NSGS', 1, comp_file)


class SiconosWrappedSolver(SiconosSolver):
    def __call__(self, problem, reactions, velocities):
        return self._API(problem, reactions, velocities, self._SO)
