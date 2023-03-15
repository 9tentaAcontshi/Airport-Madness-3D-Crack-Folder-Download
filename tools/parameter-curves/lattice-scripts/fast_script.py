def n(sd):
     return (sd - (2.98154318414599))/-0.02659946234310527


def ternary_search(params_in, sds):
     """
     A fast script to find a rough parameter curve for ternary secrets
     
     USAGE:
     
     SDs = range(4,62)
     ternary_search(schemes.TFHE630, SDs)
     """

    out = []

    for sd in sds:
        i = len(out)
        try:
            n_new = out[i-1][0]
        except:
            n_new = ceil(n(-1 * sd)) 
               
        # these are the parameters to edit if we want to try something new.
        # Xe remains constant throughout the script (e.g. D(sigma)) but we could try
        # new secret distributions or moduli using this script.
        # to set the moduli, change the below line
        params_in = params_in.updated(q = 2**64)
        # to set the secret distribution, change the below line
        params_in = params_in.updated(Xs = ND.UniformMod(3))
        params_in = params_in.updated(Xe = ND.DiscreteGaussian(2**sd))
        params_in = params_in.updated(n = n_new)
        print(params_in)
        sec = LWE.dual_hybrid(params_in, red_cost_model = RC.BDGL16)

        if sec["rop"] < 2**128:
            while sec["rop"] < 2**128:
                n_new += 16
                params_in = params_in.updated(n = n_new)
                print(params_in)
                sec = LWE.dual_hybrid(params_in, red_cost_model = RC.BDGL16)
                print(sec)
                print((n_new, log(sec["rop"],2)))

            # go back one
            params_in = params_in.updated(n = params_in.n - 16)
            n_new = params_in.n - 16
            sec = LWE.dual_hybrid(params_in, red_cost_model = RC.BDGL16)

        if sec["rop"] > 2**128:
            while sec["rop"] > 2**128:
                n_new -= 16
                params_in = params_in.updated(n = n_new)
                print(params_in)
                sec = LWE.dual_hybrid(params_in, red_cost_model = RC.BDGL16)
                print(sec)
                print((n_new, log(sec["rop"],2)))

            # go forward one
            params_in = params_in.updated(n = params_in.n + 16)
            n_new = params_in.n + 16
            sec = LWE.dual_hybrid(params_in, red_cost_model = RC.BDGL16)
        
        out.append((n_new, sd - 64, log(sec["rop"],2)))
        print(out)

    return out
  
# 64-bit ternary curve for Sam
'''
[(2295, -60, 127.078792588350),
 (2311, -59, 128.488776992617),
 (2279, -58, 128.781019631495),
 (2231, -57, 128.157136569127),
 (2199, -56, 128.531273681268),
 (2167, -55, 128.979204294054),
 (2119, -54, 128.360786677986),
 (2087, -53, 128.661165611356),
 (2039, -52, 128.020440828915),
 (2007, -51, 128.402419628669),
 (1975, -50, 128.850613930224),
 (1927, -49, 128.220332344556),
 (1895, -48, 128.532995642188),
 (1863, -47, 129.053763770276),
 (1815, -46, 128.261111640544),
 (1783, -45, 128.724652308223),
 (1751, -44, 129.256346567269),
 (1703, -43, 128.427087467079),
 (1671, -42, 128.925719697154),
 (1623, -41, 128.104646125358),
 (1591, -40, 128.626307377402),
 (1559, -39, 129.177132132841),
 (1511, -38, 128.293676843984),
 (1479, -37, 128.867977371216),
 (1447, -36, 129.552753258365),
 (1399, -35, 128.535541064053),
 (1367, -34, 129.184274172714),
 (1319, -33, 128.156821623523),
 (1287, -32, 128.821384214969),
 (1255, -31, 129.488413893293),
 (1207, -30, 128.435582359883),
 (1175, -29, 129.139486913799),
 (1127, -28, 128.021991050731),
 (1095, -27, 128.743656738640),
 (1063, -26, 129.556303276407),
 (1015, -25, 128.299295159324),
 (983, -24, 129.160867181381),
 (951, -23, 130.126980330861),
 (903, -22, 128.712531288012),
 (871, -21, 129.716764897387),
 (823, -20, 128.186625256950),
 (791, -19, 129.278809944079),
 (759, -18, 130.451246885528),
 (711, -17, 128.735276164873),
 (679, -16, 130.020905694739),
 (631, -15, 128.097491424244),
 (599, -14, 129.533186291015),
 (567, -13, 131.148363008945),
 (519, -12, 128.887004678722),
 (487, -11, 130.683187631311),
 (439, -10, 128.123631777833),
 (407, -9, 130.148519324464),
 (375, -8, 132.566934205073),
 (327, -7, 129.405360689035),
 (295, -6, 132.265174113146),
 (247, -5, 128.418255227156)]

sage: a
-0.02630290701546356
sage: b
1.787718073729275

def sd(n):
     return a * n + b

sage: sd(1000)
-24.515188941734287
'''