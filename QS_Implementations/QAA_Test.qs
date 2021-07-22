namespace Quantum.QS_Implementations {
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Convert;

    
    @Test("QuantumSimulator")
    operation IQAETest () : Unit {
        let iterations = 3;
        let bmax = PI(); // 4.0;
        let shots = 500;

        mutable thetprev = 0.0;
        for i in 0..iterations {
            let arr = IQAE(2, bmax, shots, i);
            mutable tmp = 0.0;
            for j in arr {
                if j {
                    set tmp += 1.0;
                }
            }
            let prob = tmp / IntAsDouble(shots); // P|1> = sin^2((2*iterations+1)theta)
            Message($"Prob of 1 is {prob}!");
            let theta = ArcSin(Sqrt(prob)); // / IntAsDouble(2*iterations + 1);

            if i == 0 {
                set thetprev = theta;
            } else {
                mutable closest = theta;
                let solns = [theta, PI()-theta, PI()+theta, 2.0*PI()-theta]; // all solutions are theta, pi-theta, pi+theta, 2pi-theta, and those solutions + 2pi*x
                mutable multiplier = 1.0;
                for j in 1 .. 2*i {
				    if j % 4 == 0 {
                        set multiplier +=1.0;
                    }
                    let cur = (solns[j%4] * multiplier) / IntAsDouble(2*i+1);
                    Message($"Cur is: {cur}");

                    if AbsD(cur - thetprev) < AbsD(closest - thetprev) {
                        set closest = cur;
                    }

                    //let coeff = PI() * IntAsDouble(j);
                    //if AbsD(theta + IntAsDouble(j) - thetprev) < AbsD(closest - thetprev) {
                    //    set closest = theta * IntAsDouble(j);
                    //} else if AbsD(theta - IntAsDouble(j) - thetprev) < AbsD(closest - thetprev)
				}
                set thetprev = closest;
            }

            Message($"Current theta estimate: {thetprev}");
        }
        Message($"Probability of measuring correct state is: {(Sin(thetprev) ^ 2.0)}");
    }
}
