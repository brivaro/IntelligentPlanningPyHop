# domain.py
import pyhop
from collections import deque
from heapq import heappush, heappop

# Constantes de coste
COST_WALK = 1
COST_BUS = 3

def find_path_with_modes(state, graph, start, goal):
    """
    Busca la ruta desde start hasta goal considerando dos modos para cada conexión.
    Cada arista se puede transitar caminando (coste COST_WALK) o en bus (coste COST_BUS).
    Devuelve una lista de pasos: cada paso es una tupla (nodo_actual, nodo_siguiente, modo)
    que representa la acción recomendada para minimizar el coste sin exceder state.limit_cost.
    Si no existe ruta válida, retorna None.
    
    Variable graph es footmap!!!!
    """
    # Inicializamos la frontera como una cola de prioridad
    # Cada elemento de la cola es una tupla:
    #   (coste_acumulado, nodo_actual, ruta)
    # donde "ruta" es una lista de pasos, y cada paso es (de, a, bus/walk)
    frontier = [] #lista de tuplas
    #               coste  start  modos
    heappush(frontier, (0, start, []))
    
    # Guardamos en "best" el coste minimo con que se ha alcanzado cada nodo
    best = {start: 0}

    """EJEMPLO:
    method instance ('move_driver', 'D1', 'C0')
    [(0, 'C1', [])] ##apilamos el principio: estamos donde empezamos, no nos movemos
    [] # desapilamos y sacamos los vecinos de C1
    [(1, 'P_01', [('C1', 'P_01', 'walk')]), (1, 'P_12', [('C1', 'P_12', 'walk')])]
    [(1, 'P_12', [('C1', 'P_12', 'walk')])]
    [(1, 'P_12', [('C1', 'P_12', 'walk')]), (2, 'C0', [('C1', 'P_01', 'walk'), ('P_01', 'C0', 'walk')])]
    [(2, 'C0', [('C1', 'P_01', 'walk'), ('P_01', 'C0', 'walk')])]
    [(2, 'C0', [('C1', 'P_01', 'walk'), ('P_01', 'C0', 'walk')]), (2, 'C2', [('C1', 'P_12', 'walk'), ('P_12', 'C2', 'walk')])]
    [(2, 'C2', [('C1', 'P_12', 'walk'), ('P_12', 'C2', 'walk')])]
    """
    
    while frontier:
        print(frontier)
        cost, current, path = heappop(frontier)
        print(frontier)
        
        # Si hemos llegado a la meta, devolvemos la ruta (lista de pasos)
        if current == goal:
            return path
        
        # Para cada vecino del nodo actual (miro grafo footmap)
        for neighbor in graph.get(current, []):
            # --- Opción 1: transitar caminando ---
            new_cost = cost + COST_WALK
            # Solo consideramos esta opción si no se excede el límite
            if new_cost <= state.limit_cost:
                # Si este vecino no se ha alcanzado antes o se alcanza con menor coste, actualizamos:
                if neighbor not in best or new_cost < best[neighbor]:
                    best[neighbor] = new_cost
                    heappush(frontier, (new_cost, neighbor, path + [(current, neighbor, 'walk')]))
            
            # --- Opción 2: transitar en bus ---
            new_cost = cost + COST_BUS
            if new_cost <= state.limit_cost:
                if neighbor not in best or new_cost < best[neighbor]:
                    best[neighbor] = new_cost
                    heappush(frontier, (new_cost, neighbor, path + [(current, neighbor, 'bus')]))
    
    # Si se termina la exploración sin llegar a la meta, devolvemos None
    return None

##################################################
# Definición de Operadores

def assign_driver_op(state, driver, truck):
    if state.loc[driver] == state.loc[truck] and state.driver_of[truck] is None:
        state.driver_of[truck] = driver
        return state
    return False

def remove_driver_op(state, driver, truck):
    if state.driver_of[truck] == driver and state.loc[driver] == state.loc[truck]:
        state.driver_of[truck] = None
        return state
    return False

def drive_truck_op(state, truck, city_from, city_to):
    driver = state.driver_of[truck]
    if driver is not None:
        # Comprobamos ubicaciones y carreteras
        if (state.loc[truck] == city_from and 
            state.loc[driver] == city_from and 
            city_to in state.roadmap[city_from]):
            # Actualizamos ubicación
            state.loc[truck] = city_to
            state.loc[driver] = city_to
            return state
    return False

def walk_op(state, driver, city_from, city_to):
    if state.loc[driver] == city_from and city_to in state.footmap[city_from]:
         if state.cost + COST_WALK > state.limit_cost:
             return False  # No se permite exceder el coste
         state.loc[driver] = city_to
         state.cost += COST_WALK
         return state
    return False

def bus_op(state, driver, city_from, city_to):
    if state.loc[driver] == city_from and city_to in state.footmap[city_from]:
         if state.cost + COST_BUS > state.limit_cost:
             return False  # No se permite exceder el coste
         state.loc[driver] = city_to
         state.cost += COST_BUS
         return state
    return False

def load_op(state, package, truck):
    driver = state.driver_of[truck]
    if (state.loc[package] == state.loc[truck] and 
        driver is not None and 
        state.loc[driver] == state.loc[truck] and
        state.pack_in[package] is None):
        state.pack_in[package] = truck
        return state
    return False

def unload_op(state, package, truck):
    driver = state.driver_of[truck]
    if (state.pack_in[package] == truck and
        state.loc[truck] == state.loc[driver] and
        state.driver_of[truck] is not None):
        # El paquete pasa a estar en la ciudad del camión
        city = state.loc[truck]
        state.loc[package] = city
        state.pack_in[package] = None
        return state
    return False

def update_final_cost(state, cost):
    state.limit_cost = cost # establecemos nuestra variable coste limite
    return state

# Declarar operadores
pyhop.declare_operators(
    assign_driver_op, remove_driver_op, drive_truck_op, 
    walk_op, bus_op, load_op, unload_op, update_final_cost
)

##################################################
# Definición de Métodos

def method_final_cost(state, cost):
    return [('update_final_cost', cost)]
    
def method_move_truck(state, truck, city_dest):
    city_truck = state.loc[truck]
    
    # Caso base: si el truck ya en el destino, no se hace nada
    if city_truck == city_dest:
        return []
    
    # Si el truck no tiene conductor, intentamos asignarle uno
    if state.driver_of[truck] is None:
        # Buscar conductores disponibles en la misma ciudad
        drivers_here = [d for d in state.drivers 
                        if state.loc[d] == city_truck and d not in state.driver_of.values()]
        if drivers_here:
            # Si hay alguno, asignamos el primero y continuamos
            return [
                ('assign_driver_op', drivers_here[0], truck),
                ('move_truck', truck, city_dest)
            ]
        else:
            # Si no hay conductores en la misma ciudad, se busca uno en otra ciudad
            for d in state.drivers:
                if state.loc[d] != city_truck and d not in state.driver_of.values():
                    return [
                        ('move_driver', d, city_truck),
                        ('assign_driver_op', d, truck),
                        ('move_truck', truck, city_dest)
                    ]
            # Si no se encuentra ningún conductor disponible, fallamos.
            return False
    
    # Si el camión ya tiene conductor, procedemos a moverlo.
    # Comprobamos si el destino es alcanzable en un solo salto.
    if city_dest in state.roadmap[city_truck]:
        # Movimiento directo.
        return [('drive_truck_op', truck, city_truck, city_dest)]
    else:
        # Se requiere pasar por una ciudad intermedia.
        # Elegimos (por ejemplo) la primera ciudad vecina y actuamos de forma recursiva.
        for city_next in state.roadmap[city_truck]:
            return [
                ('drive_truck_op', truck, city_truck, city_next),
                ('move_truck', truck, city_dest)
            ]
        # En caso poco probable de que no haya vecinos, fallamos.
        return False
 
def method_move_driver(state, driver, city_dest):
    location = state.loc[driver]
    
    # Caso base: el driver ya en el destino
    if location == city_dest:
        return []
    
    # Buscamos si el driver esta asignado a algún truck, porque hay que bajarlo antes
    truck = None
    for t in state.trucks:
        if state.driver_of[t] == driver:
            truck = t
            break

    # Calculamos el camino desde la pos actual hasta el destino caminando o bus
    # ESTO evita bucles infinitos de caminar de un lugar a otro
    removal_step = []
    if truck is not None:
        removal_step = [('remove_driver_op', driver, truck)]
    
    # Usamos la función para obtener la ruta óptima con modos
    route = find_path_with_modes(state, state.footmap, location, city_dest)
    if not route or len(route) == 0:
        return False  # No existe ruta válida
    
    # Tomamos el primer tramo de la ruta
    first_step = route[0]  # (location, next_loc, mode)
    _, next_loc, mode = first_step
    if mode == 'bus':
        move_op = ('bus_op', driver, location, next_loc)
    else:
        move_op = ('walk_op', driver, location, next_loc)
    
    # Continuamos de forma recursiva hasta llegar a city_dest
    return removal_step + [move_op, ('move_driver', driver, city_dest)]

def method_transport_package(state, package, city_dest):
    current_city = state.loc[package]
    
    # Caso base
    if current_city == city_dest:
        return []
    
    # Si el paquete NO en truck
    if state.pack_in[package] is None:
        trucks_here = [t for t in state.trucks if state.loc[t] == current_city]
        if not trucks_here: # no hay camiones, llamar a un driver
            for t in state.trucks:
                # Si el truck ya tiene conductor y no tiene paquete, lo movemos
                if state.driver_of[t] is not None and t not in state.pack_in.values():
                    return [
                        ('move_truck', t, current_city),
                        ('transport_package', package, city_dest)
                    ]
                # Si no tiene driver, buscamos uno en la misma ciudad que este disponible
                drivers_there = [d for d in state.drivers if state.loc[d] == state.loc[t] and 
                                 d not in state.driver_of.values()]
                if drivers_there:
                    return [
                        ('assign_driver_op', drivers_there[0], t),
                        ('move_truck', t, current_city),
                        ('transport_package', package, city_dest)
                    ]
                # No hay conductor en la ciudad del truck --> traer driver disponible de fuera
                for d in state.drivers:
                    if state.loc[d] != state.loc[t] and d not in state.driver_of.values():
                        return [
                            ('move_driver', d, state.loc[t]),
                            ('assign_driver_op', d, t),
                            ('move_truck', t, current_city),
                            ('transport_package', package, city_dest)
                        ]
                return False
        truck_chosen = trucks_here[0]
        
        # Comprobar si el truck ya tiene driver
        if state.driver_of[truck_chosen] is None:
            # Primero, buscamos si hay un conductor disponible en la misma ciudad
            for d in state.drivers:
                if state.loc[d] == current_city and d not in state.driver_of.values():
                    # Asignamos directamente este conductor al truck
                    return [
                        ('assign_driver_op', d, truck_chosen),
                        ('transport_package', package, city_dest)
                    ]
            
            # Si no encontramos a nadie en la ciudad, entonces buscamos un conductor fuera
            for d in state.drivers:
                if state.loc[d] != current_city and d not in state.driver_of.values():
                    return [
                        ('move_driver', d, current_city),
                        ('assign_driver_op', d, truck_chosen),
                        ('transport_package', package, city_dest)
                    ]
            
            # Si no hay ningún conductor en todo el estado que podamos mover, fallamos
            return False
        else:
            # Truck con conductor: cargamos el paquete
            return [
                ('load_op', package, truck_chosen),
                ('transport_package', package, city_dest)
            ]
    else:
        # El paquete en un truck
        truck_carrying = state.pack_in[package]  # truck que lleva el paquete
        city_truck = state.loc[truck_carrying]    # ciudad donde se encuentra el truck

        # Si el truck no tiene driver, porque ha bajado ha caminar, lo asignamos antes de moverlo
        if state.driver_of[truck_carrying] is None:
            # buscamos driver en la ciudad
            drivers_here = [d for d in state.drivers if state.loc[d] == city_truck and 
                             d not in state.driver_of.values()]
            if drivers_here:
                return [
                    ('assign_driver_op', drivers_here[0], truck_carrying),
                    ('transport_package', package, city_dest)
                ]
            
            # Se han bajado del truck, esta parado, buscar un driver de fuera
            for d in state.drivers:
                if state.loc[d] != city_truck and d not in state.driver_of.values():
                    return [
                        ('move_driver', d, city_truck),
                        ('assign_driver_op', d, truck_carrying),
                        ('transport_package', package, city_dest)
                    ]
            return False

        # Si el truck con driver aun no es el destino, se mueve
        if city_truck != city_dest:
            return [
                ('move_truck', truck_carrying, city_dest),
                ('transport_package', package, city_dest)
            ]
        else:
            # Hemos llegado al destino, descargamos el paquete
            return [('unload_op', package, truck_carrying)]

# Declarar métodos en PyHop
pyhop.declare_methods('move_truck', method_move_truck)
pyhop.declare_methods('move_driver', method_move_driver)
pyhop.declare_methods('transport_package', method_transport_package)
pyhop.declare_methods('final_cost', method_final_cost)

# Imprimir operadores y métodos para verificación
if __name__ == '__main__':
    print("\nOPERADORES:")
    pyhop.print_operators()
    print("\nMÉTODOS:")
    pyhop.print_methods()
