import os
os.makedirs('data', exist_ok=True)
from backend.core.memory import Memory
from backend.core.creature import CreatureState

m = Memory()
print(f'Days alive: {m.days_alive()}')

c = CreatureState()
print(f'State before stimulus: {c.current_state}')
c.apply_stimulus('build_failure', 1.0)
c.apply_stimulus('build_failure', 1.0)
c.apply_stimulus('build_failure', 1.0)
print(f'Stress after 3 failures: {c.vars["stress"]:.3f}')
new_state = c._resolve_state()
print(f'Resolved state: {new_state}')
m.save_vars(c.vars_dict())
print('Memory saved OK')

# Test loading back
c2 = CreatureState(saved=m.load_vars())
print(f'Stress after reload: {c2.vars["stress"]:.3f}')
m.close()
print('All checks passed!')
