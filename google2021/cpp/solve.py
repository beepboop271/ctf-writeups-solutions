# almost entirely based off of https://github.com/angr/angr-doc/blob/master/examples/b01lersctf2020_little_engine/solve.py

import angr
import claripy

p = angr.Project("cpp")

flag_chars = [claripy.BVS(f"flag_{i}", 8) for i in range(27)]
flag = claripy.Concat(*(flag_chars + [claripy.BVV(b"\n")]))

st = p.factory.entry_state(
    args=["./cpp"],
    add_options=angr.options.unicorn,
    stdin=flag,
)

for k in flag_chars:
    st.solver.add(k >= ord("0"))
    st.solver.add(k <= ord("}"))

sm = p.factory.simulation_manager(st)
sm.run()

for x in sm.deadended:
    if b"win" in x.posix.dumps(1):
        print(x.posix.dumps(0))
