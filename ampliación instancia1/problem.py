# problem.py
import pyhop
import domain  # import our domain (operators, methods)

def main():
    # Our world
    state0 = pyhop.State('initial_state')
    
    # Objects
    state0.cities   = ['C0', 'C1', 'C2']
    state0.drivers  = ['D1', 'D2', 'D3']
    state0.trucks   = ['T1', 'T2', 'T3']
    state0.packages = ['P1', 'P2', 'P3']
    # state0.middle_points = ['P_01', 'P_12']

    # Locations
    ##### ¿change to state0.loc = {'C0': [objects]...}? 
    ##### NO! it is not efficient for our problem
    state0.loc = {
        'D1': 'P_01',
        'D2': 'C1',
        'T1': 'C1',
        'T2': 'C0',
        'P1': 'C0',
        'P2': 'C0',
        'D3': 'C2',
        'T3': 'C0',
        'P3': 'C1',
    }

    # Driver of X truck
    state0.driver_of = {
        'T1': None,
        'T2': None,
        'T3': None,
    }

    # In which truck is my package?
    state0.pack_in = {
        'P1': None,
        'P2': None,
        'P3': None,
    }

    # Roadmap for trucks
    state0.roadmap = {
        'C0': ['C1', 'C2'],       # C0 connect C1
        'C1': ['C0', 'C2'], # C1 connect C0 and C2
        'C2': ['C1', 'C0']        # C2 connect C1
    }

    # Rootmap/pathways for drivers to walk and take buses
    state0.footmap = {
        'C0': ['P_01'],         #  - C0   connect P_01
        'P_01': ['C0', 'C1'],   #  - P_01 connect C0    and C1
        'C1': ['P_01', 'P_12'], #  - C1   connect P_01  and P_12
        'P_12': ['C1', 'C2'],   #  - P_12 connect C1    and C2
        'C2': ['P_12']          #  - C2   connect P_12
    }

    state0.cost = 0

    # Goals (HTN - Hierarchical Task Network) == tasks to do
    # example:
    # GOAL
    tasks = [
        ('final_cost', 10),
        ('transport_package', 'P1', 'C1'), #  - transport P1 to C1
        ('transport_package', 'P2', 'C2'), #  - transport P2 to C2
        ('transport_package', 'P3', 'C0'), 
        ('move_truck', 'T1', 'C0'),        #  - move T1 to C0
        ('move_truck', 'T2', 'C1'),
        ('move_truck', 'T3', 'C2'),
        ('move_driver', 'D1', 'C0'),       #  - move D1 to C0
        ('move_driver', 'D3', 'C0'),
    ]

    goal1 = pyhop.Goal('goal1')
    goal1.tasks = tasks

    print("\nInitial state:")
    pyhop.print_state(state0)
    print("\nTasks to planificate:")
    print(tasks)

    plan = pyhop.pyhop(state0, goal1.tasks, verbose=3)

    print("\nPlanning operator by PyHop:")
    if plan:
        for step in plan[0]:
            print("  ", step)
    else:
        print("No planning!")

# execute problem.py to run de problem
if __name__ == '__main__':
    main()
