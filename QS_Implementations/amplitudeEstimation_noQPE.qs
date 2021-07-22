namespace Quantum.QS_Implementations {

    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Math;


    operation amplitudeEstimation (regsize: Int, iterations: Int, shots: Int, A: (Qubit[], Qubit, Double[]) => Unit is Adj, args: Double[]) : Bool[] { // todo: double check oreder of parameters conform to style
        // from "Quantum amplitude estimation algorithms on IBM quantum devices" Rao et al. with methods from Suzuki et al.
        // https://arxiv.org/pdf/2008.02102.pdf

        mutable arr = new Bool[0];

        use (register, ancilla) = (Qubit[regsize], Qubit()) {
            for i in 0..shots-1 {
                // A
                A(register, ancilla, args);

                for j in 0..iterations-1 {
                    // Q = A S_0 A^-1 S_x
                    // note: because quantum operations are like matrices, operations are applied right-to-left
                    Q_Grover(register, ancilla, A, args);
                }

                set arr += [ResultAsBool(M(ancilla))];
                ResetAll([ancilla] + register);
			}
        }
        return arr;
    }

    /// # Summary
    /// Unitary operator that computes the definite integral of sin^2(x) from 0 to b with a Riemann sum.
    ///
    /// # Input
    /// ## register
    /// Qubit register -- The Riemann sum uses 2^n subintervals, where n is the length of the qubit register. 
    /// ## ancilla
    /// Ancilla qubit
    /// ## args
    /// 1st argument should be upper bound of the integral, and 2nd argument should be 0, 0.5 or 1 for left, midpoint, or right Riemann sum, respectively (defaults to left Riemann sum).
    operation intSinSq (register: Qubit[], ancilla: Qubit, args: Double[]) : Unit is Adj {
        let len = Length(register);
        let bmax = args[0];

        ApplyToEachA(H, register);
        if args[1] == 0.5 or args[1] == 1.0 {
            Ry((args[1] * bmax) / IntAsDouble(2^len), ancilla);
        }

        for i in 0..len-1 {
            Controlled Ry([register[i]], (bmax / IntAsDouble(2^(len-1-i)), ancilla));
        }
    }

    operation Q_Grover(register: Qubit[], ancilla: Qubit, A: (Qubit[], Qubit, Double[]) => Unit is Adj, args: Double[]) : Unit {
        // S_x
        Z(ancilla);

        // A^-1
        Adjoint A(register, ancilla, args);

        // 0-Controlled Z, S_0
        ApplyToEach(X, register+[ancilla]);
        Controlled Z(register, ancilla);
        ApplyToEach(X, register+[ancilla]);

        // A
        A(register, ancilla, args);
    }
}
