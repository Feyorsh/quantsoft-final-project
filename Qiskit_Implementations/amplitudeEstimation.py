from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute
from qiskit import Aer

import math

def amplitudeEstimation():
    iterations = 15
    shots = 500
    qsize = 4
    exponential = False

    sim = Aer.get_backend('aer_simulator')

    A = intSinSq
    Aadj = AintSinSq
    args = [85.6 * math.pi / 4, 1]

    register = QuantumRegister(qsize)
    target = QuantumRegister(1)
    measure = ClassicalRegister(1)
    circ = QuantumCircuit(register, target, measure)

    A(circ, register, target, args)
    circ.measure(target, measure)

    prob = run(circ, shots, sim)
    thetprev = math.asin(math.sqrt(prob))

    for i in range(1, iterations+1):
        circ.data.pop() # remove measure gate
        if exponential:
            if i == 1:
                Q_Grover(circ, register, target, A, Aadj, args)
            else:
                for j in range(2 ** (i-2)):
                    Q_Grover(circ, register, target, A, Aadj, args)
        else:
            Q_Grover(circ, register, target, A, Aadj, args)
        circ.measure(target, measure)

        prob = run(circ, shots, sim)
        theta = math.asin(math.sqrt(prob))
        solns = [theta, math.pi - theta, math.pi + theta, 2 * math.pi - theta]

        closest = theta / (2*i+1)
        multiplier = 0

        for j in range(1, 2*i):
            if j % 4 == 0:
                multiplier += 1

            t = (solns[j%4] + multiplier * (2*math.pi)) / (2*i+1)

            if abs(t - thetprev) < abs(closest - thetprev):
                closest = t

        thetprev = closest

    print("Probability is: " + str(math.sin(thetprev)**2))

def run(circuit, shots, simulator):
    result = execute(circuit, simulator, shots=shots).result()
    counts = result.get_counts(circuit)

    return counts['1'] / shots


"""
def amplitudeEstimation(circuit, qregister, ancilla, cregister, iterations, shots, A, args):
    # from "Quantum amplitude estimation algorithms on IBM quantum devices" Rao et al. with methods from Suzuki et al.
    # https://arxiv.org/pdf/2008.02102.pdf
    
    if iterations == 0:
        A(circuit, qregister, ancilla, args)


    for j in range(iterations):
        # Q = A S_0 A^-1 S_x
        # note: because quantum operations are like matrices, operations are applied right-to-left
        Q_Grover(circuit, qregister, ancilla, A, args)
    
    # measure ancilla into "measurement" after iterations of Q_Grover
    circuit.measure(ancilla, measurement)
    # set up simulator with "shots" shots
    simulator = Aer.get_backend('aer_simulator')
    simulation = execute(circuit, simulator, shots=shots)
    # get result of measuring it "shots" times, put it indictionary form, unpack in for loop
    result = simulation.result()
    counts = result.get_counts(circuit)
    # measured states will be only 1s and 0s since we only measure the ancilla
    for(measured_state, count) in counts.items():
        if measured_state == "1":
            onesMeasured = count

    return onesMeasured
"""

def intSinSq(circuit, register, ancilla, args):
    """
    # Summary
    Unitary operator that computes the definite integral of sin^2(x) from 0 to b with a Riemann sum.

    # Input
    ## register
    Qubit register -- The Riemann sum uses 2^n subintervals, where n is the length of the qubit register. 
    ## ancilla
    Ancilla qubit
    ## args
    1st argument should be upper bound of the integral, and 2nd argument should be 0, 0.5 or 1 for left, midpoint, or right Riemann sum, respectively (defaults to left Riemann sum).
    """
    
    length = len(register)
    bmax = args[0]

    circuit.h(register)
    if args[1] == 0.5 or args[1] == 1.0:
        circuit.ry((args[1] * bmax) / (2**length), ancilla)

    for i in range(length):
        circuit.cry(bmax / (2**(length-1-i)), register[i], ancilla)

def AintSinSq(circuit, register, ancilla, args):
    length = len(register)
    bmax = args[0]

    for i in reversed(range(length)):
        circuit.cry(-bmax / (2**(length-1-i)), register[i], ancilla)

    if args[1] == 0.5 or args[1] == 1.0:
        circuit.ry((-args[1] * bmax) / (2**length), ancilla)
    circuit.h(register)


def Q_Grover(circuit, register, ancilla, A, Aadj, args): 
	# S_x
    circuit.z(ancilla)

    # A^-1
    Aadj(circuit, register, ancilla, args)

    # 0-controlled Z
    circuit.x(register)
    circuit.x(ancilla)
    circuit.h(ancilla)
    circuit.mcx(register, ancilla, mode='noancilla')
    circuit.h(ancilla)
    circuit.x(ancilla)
    circuit.x(register)

    # A
    A(circuit, register, ancilla, args)

amplitudeEstimation()