from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.providers.aer import AerSimulator
from qiskit import IBMQ
from qiskit.compiler import transpile
from time import perf_counter
import math

import amplitudeEstimation

def constructionTime(iterations, exponential):
    qsize = 2
    A = amplitudeEstimation.intSinSq
    Aadj = amplitudeEstimation.AintSinSq
    args = [2 * math.pi / 3, 0.5]

    # initialization
    register = QuantumRegister(qsize)
    target = QuantumRegister(1)
    measure = ClassicalRegister(1)
    circ = QuantumCircuit(register, target, measure)

    #building
    start = perf_counter()

    A(circ, register, target, args)
    circ.measure(target, measure)
    circ_ls = [circ]

    for i in range(1, iterations+1):
        circ.data.pop() # remove measure gate
        if exponential:
            if i == 1:
                amplitudeEstimation.Q_Grover(circ, register, target, A, Aadj, args)
            else:
                for j in range(2 ** (i-2)):
                    amplitudeEstimation.Q_Grover(circ, register, target, A, Aadj, args)
        else:
            amplitudeEstimation.Q_Grover(circ, register, target, A, Aadj, args)
        circ.measure(target, measure)
        circ_ls.append(circ)

    end = perf_counter()

    print(f"Creating {len(circ_ls)} circuits took {(end-start)} sec.")
    return circ_ls

def compileTime(circ_ls, backend_name):
    if not IBMQ.active_account():
        global provider
        provider = IBMQ.load_account()
    backend = provider.get_backend(backend_name)
    new_circs = []

    start = perf_counter()
    for i in circ_ls:
        new_circs.append(transpile(i, backend=backend, optimization_level=1))
    end = perf_counter()

    print(f"Transpiling {len(circ_ls)} circuits for {backend_name} took {(end - start)} seconds.")
    return new_circs

def gateCount(circuit):
    d = circuit.count_ops()
    if "barrier" in d:
        del d["barrier"]
    if "snapshot" in d:
        del d["snapshot"]

    count = 0
    tl = []
    for k, v in d.items():
        count += v
        if k[0] == 'c':
            tl.append((k, v))

    print(f"Max gate count: {count}")
    if tl:
        print(f"Additionally, there are ", end='')
        it = iter(tl)
        t = next(it)
        if len(tl) == 1:
            print(f"{t[1]} {t[0]} gates.")
        else:
            for k, v in it:
                print(f"{v} {k} gates, ", end='')
            print(f"& {t[1]} {t[0]} gates.")
    

def metrics(iters, exponential, sim_name):
    print(f"Analyzing circuit with k = {iters} and {'exponential' if exponential else 'linear'} growth.\n")

    print("Metrics for original circuit:\n")
    circ_ls = constructionTime(iters, exponential)
    print(f"Max depth: {circ_ls[-1].depth()}")
    print(f"Max width: {circ_ls[-1].width()}")
    gateCount(circ_ls[-1])

    print(f"\nMetrics for transpiled circuit ({sim_name}):\n")
    new_circs = compileTime(circ_ls, "ibmq_lima")
    print(f"Max depth: {new_circs[-1].depth()}")
    print(f"Max width: {new_circs[-1].width()}")
    gateCount(new_circs[-1])

    print("\n")



simulator = "ibmq_lima"
k_linear = [3, 5, 7]
k_exponential = [1, 2, 3]

for i in k_linear:
    metrics(i, False, "ibmq_lima")

for i in k_exponential:
    metrics(i, True, "ibmq_lima")