from pipeline import step1, step2, step2_gpumd, step3, step4, step5, step6

#step2.minimize_polycrystal({'projname': 'test'}, "dump.xyz", "UNEP_v1.txt", [], None, 'en')
d = {'projname': 'AgW'}

step2_gpumd.make_orthogonal(d, 'Ag_10nm_initmin.xyz')