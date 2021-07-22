namespace Quantum.QS_Implementations {
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Convert;

    
    @Test("QuantumSimulator")
    operation QAE_Test () : Unit {
        let iterations = 7;
        let shots = 500;

        let A = intSinSq;
        let args = [263.6*PI(), 1.0]; // for A

        mutable thetprev = 0.0;
        for i in 0..iterations {
            let arr = amplitudeEstimation(4, i, shots, A, args);

            mutable tmp = 0.0;
            for j in arr {
                if j {
                    set tmp += 1.0;
                }
            }

            let prob = tmp / IntAsDouble(shots); // P|1> = sin^2((2*i+1)theta)
            Message($"Prob of 1 is {prob}!");
            let theta = ArcSin(Sqrt(prob));
            Message($"Fat theta: {theta}");

            if i == 0 {
                set thetprev = theta;
            } else {
                mutable closest = theta / IntAsDouble(2*i+1);
                let solns = [theta, PI()-theta, PI()+theta, 2.0*PI()-theta]; // all solutions are theta, pi-theta, pi+theta, 2pi-theta, and those solutions + 2pi*x
                
                mutable multiplier = 0.0;
                for j in 1 .. 2*i {
				    if j % 4 == 0 {
                        set multiplier +=1.0;
                    }

                    let t = (solns[j%4] + multiplier*2.0*PI()) / IntAsDouble(2*i+1);
                    Message($"Cur is: {t}");

                    if AbsD(t - thetprev) < AbsD(closest - thetprev) {
                        set closest = t;
                    }
				}
                set thetprev = closest;
            }

            Message($"Current theta estimate: {thetprev}");
        }
        Message($"Probability of measuring correct state is: {(Sin(thetprev) ^ 2.0)}");
    }
}
