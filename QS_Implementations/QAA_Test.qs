namespace Quantum.QS_Implementations {
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Convert;

    
    @Test("QuantumSimulator")
    operation IQAETest () : Unit {
        let iterations = 15;
        let bmax = PI() / 4.0;
        let shots = 500;

        mutable thetprev = 0.0;
        for i in 0..iterations {
            let arr = IQAE(3, bmax, shots, i);
            mutable tmp = 0.0;
            for j in arr {
                if j {
                    set tmp += 1.0;
                }
            }
            let prob = tmp / IntAsDouble(shots); // P|1> = sin^2((2*iterations+1)theta)
            Message($"Prob of 1 is {prob}!");
            let theta = ArcSin(Sqrt(prob)) / IntAsDouble(2*iterations + 1);

            if i == 0 {
                set thetprev = theta;
            } else {
                mutable closest = theta;
                for j in 1 .. 2*iterations+1 {
                    if AbsD(theta * IntAsDouble(j) - thetprev) < AbsD(closest - thetprev) {
                        set closest = theta * IntAsDouble(j);
                    }
				}
                set thetprev = closest;
            }

            Message($"Current theta estimate: {thetprev}");
        }
        Message($"Probability of measuring correct state is: {Sin(thetprev) ^ 2.0}");
    }
}
