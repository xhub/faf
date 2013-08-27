#!/usr/bin/env python

# Siconos-sample, Copyright INRIA 2005-2013.
# Siconos is a program dedicated to modeling, simulation and control
# of non smooth dynamical systems.
# Siconos is a free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# Siconos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Siconos; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# Contact: Vincent ACARY, siconos-team@lists.gforge.fr
#

from Siconos.Kernel import \
     Model, Moreau, TimeDiscretisation,\
     FrictionContact, NewtonImpactFrictionNSL

from Siconos.Mechanics.ContactDetection.Bullet import IO, \
    btConvexHullShape, btVector3, btCollisionObject, \
    btBoxShape, btQuaternion, btTransform, btConeShape, \
    BulletSpaceFilter, cast_BulletR, \
    BulletWeightedShape, BulletDS, BulletTimeStepping

    #import output

import shlex
import random

from numpy import zeros
from numpy.linalg import norm

import getopt



t0 = 0       # start time
T = 10.      # end time
h = 0.0005    # time step

g = 9.81     # gravity

theta = 0.51  # theta scheme

#
# Model
#
model = Model(t0, T)

#
# Simulation
#
# (4) non smooth law
nslaw = NewtonImpactFrictionNSL(0., 0., 0.3, 3)

# (1) OneStepIntegrators
osi = Moreau(theta)

static_cobjs = []


# (2) Time discretisation --
timedisc = TimeDiscretisation(t0, h)

# (3) one step non smooth problem
osnspb = FrictionContact(3)

nopts = osnspb.numericsOptions()
nopts.verboseMode = 0
nopts.outputMode = 0
nopts.fileName = "model"
nopts.title = "model"
nopts.description = "Bullet Bouncing Box"
nopts.math_info = "Moreau TimeStepping, h=0.005, theta =0.5"

print osnspb.numericsOptions().outputMode

osnspb.numericsSolverOptions().iparam[0] = 100000
osnspb.numericsSolverOptions().dparam[0] = 1e-8
osnspb.setMaxSize(16384)
osnspb.setMStorageType(1)
#osnspb.setNumericsVerboseMode(False)

# keep previous solution
osnspb.setKeepLambdaAndYState(True)

# (5) broadphase contact detection
broadphase = BulletSpaceFilter(model, nslaw)

# (6) Simulation setup with (1) (2) (3) (4) (5)
simulation = BulletTimeStepping(timedisc, broadphase)
simulation.insertIntegrator(osi)
simulation.insertNonSmoothProblem(osnspb)
simulation.setNewtonMaxIteration(2)


k = 1

# time loop


with IO.Dat(broadphase, osi) as io:

    model.initialize(simulation)

    io.outputStaticObjects()
    io.outputDynamicObjects()
    while(simulation.hasNextEvent()):

        print 'contact detection', k
        broadphase.buildInteractions(model.currentTime())

        print 'computeOneStep'
        simulation.computeOneStep()

        io.outputDynamicObjects()
        io.outputContactForces()

        print 'nextStep'
        simulation.nextStep()
        k += 1


