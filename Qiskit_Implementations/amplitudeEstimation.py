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

    if '1' in counts.keys():
        return counts['1'] / shots
    else:
        return 0

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