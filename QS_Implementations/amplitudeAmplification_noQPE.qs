namespace Quantum.QS_Implementations {

    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Math;


    operation IQAE (regsize: Int, bmax: Double, shots: Int, iterations: Int) : Bool[] { // check if style dictates parameter order
        // from https://link.springer.com/article/10.1007%2Fs11128-019-2565-2#Sec3
        // expects register in state |00...0>
        mutable arr = new Bool[0];

        use (register, ancilla) = (Qubit[regsize], Qubit()) {
            for i in 0..shots-1 {
                ApplyToEach(H, register); // P
                Rop(register, ancilla, bmax);

                for j in 0..iterations {
                    Q_Grover(register, ancilla, bmax);
                }

                set arr += [ResultAsBool(M(ancilla))];
                ResetAll([ancilla] + register); // does register need to be reset here?
			}
        }
        return arr;
    }

    // this was supposed to be a controlled operator, but this is considered a *bad* conventional approach because it uses a bunch of CNOTS
    operation CamplitudeAmplification (register: Qubit[], bmax: Double) : Unit { // circuit diagram has control as being |0>, but maybe it should be a parameter?
        use (ancilla, control) = (Qubit(), Qubit()) {
            ApplyToEach(H, register + [control]);
            Rop(register, ancilla, bmax);

            // loop n times?
            Controlled Q_Grover([control], (register, ancilla, bmax));

            // circuit diagram says iQFT here... but only displays H
            H(control);
            
            let ans = M(control) == One ? 1 | 0;
            Reset(control);
        }
    }

    operation Rop (register: Qubit[], ancilla: Qubit, bmax: Double) : Unit is Adj + Ctl { // This is supposed to be the unitary A operator... an oracle of sorts.
        let len = Length(register);
        Ry(bmax / IntAsDouble(2^len), ancilla);
        for i in 0..len-1 {
            Controlled Ry([register[i]], (bmax / IntAsDouble(2^(len-1-i)), ancilla));
        }
    }

    operation Q_Grover(register: Qubit[], ancilla: Qubit, bmax: Double) : Unit is Ctl {
        Z(ancilla);
        // U_I
        Adjoint Rop(register, ancilla, bmax);
        ApplyToEachC(H, register);

        X(ancilla);
        ApplyToEachC(X, register);
        H(ancilla);
        Controlled X(register, ancilla);
        H(ancilla);
        ApplyToEachC(X, register);
        X(ancilla);

        ApplyToEachC(H, register);
        Rop(register, ancilla, bmax);
    }
}
