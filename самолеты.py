import math
import heapq

class City:
    def __init__(self, name: str, lat: float, lon: float, has_fuel: bool = False):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.has_fuel = has_fuel
    
    def __repr__(self):
        return f"City({self.name})"
    
    def __eq__(self, other):
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)

class Edge:
    def __init__(self, city1: City, city2: City, distance_km: float, 
                 headwind: bool = False, fairwind: bool = False, closed: bool = False):
        self.city1 = city1
        self.city2 = city2
        self.distance_km = distance_km
        self.headwind = headwind
        self.fairwind = fairwind
        self.closed = closed
    
    def get_other_city(self, city: City) -> City:
        if city == self.city1:
            return self.city2
        elif city == self.city2:
            return self.city1
        else:
            raise ValueError("City not connected to this edge")

class Plane:
    def __init__(self, tank_capacity: int, fuel_consumption: float, cruise_speed: int):
        self.tank_capacity = tank_capacity
        self.fuel_consumption = fuel_consumption
        self.cruise_speed = cruise_speed

class Graph:
    def __init__(self):
        self.cities: dict[str, City] = {}
        self.edges: list[Edge] = []
    
    def add_city(self, city: City):
        self.cities[city.name] = city
    
    def add_edge(self, edge: Edge):
        self.edges.append(edge)
    
    def get_edges_from_city(self, city: City) -> list[Edge]:
        result = []
        for edge in self.edges:
            if edge.city1 == city or edge.city2 == city:
                result.append(edge)
        return result

class RoutePlanner:
    def __init__(self, graph: Graph, plane: Plane):
        self.graph = graph
        self.plane = plane
    
    def haversine_distance(self, city1: City, city2: City) -> float:
        R = 6371
        
        lat1_rad = math.radians(city1.lat)
        lon1_rad = math.radians(city1.lon)
        lat2_rad = math.radians(city2.lat)
        lon2_rad = math.radians(city2.lon)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distance = R * c
        return math.ceil(distance)
    
    def calculate_edge_time_and_fuel(self, edge: Edge, current_fuel: int) -> tuple[float, int]:
        if edge.closed:
            return float('inf'), 0

        if edge.headwind:
            speed_multiplier = 0.80
            fuel_multiplier = 1.20
        elif edge.fairwind:
            speed_multiplier = 1.10
            fuel_multiplier = 0.90
        else:
            speed_multiplier = 1.00
            fuel_multiplier = 1.00
        
        effective_speed = self.plane.cruise_speed * speed_multiplier
        effective_consumption = self.plane.fuel_consumption * fuel_multiplier

        time_hours = edge.distance_km / effective_speed
        fuel_needed = edge.distance_km * effective_consumption

        if fuel_needed > current_fuel:
            return float('inf'), 0

        time_hours = math.ceil(time_hours * 10) / 10
        
        return time_hours, int(fuel_needed)
    
    def a_star_search(self, start_city_name: str, target_city_name: str) -> dict:
        if start_city_name not in self.graph.cities or target_city_name not in self.graph.cities:
            return {"error": "City not found"}
        
        start_city = self.graph.cities[start_city_name]
        target_city = self.graph.cities[target_city_name]

        initial_fuel = self.plane.tank_capacity
        g_score = 0.0
        h_score = self.haversine_distance(start_city, target_city) / self.plane.cruise_speed
        f_score = g_score + h_score
        
        open_set = [(f_score, g_score, start_city, initial_fuel, [start_city], 0)]

        visited = {}
        visited_key = (start_city, initial_fuel)
        visited[visited_key] = g_score
        
        while open_set:
            current_f, current_g, current_city, current_fuel, current_path, refuel_count = heapq.heappop(open_set)

            if current_city == target_city:
                return self._build_result(current_path, current_g, refuel_count)

            for edge in self.graph.get_edges_from_city(current_city):
                next_city = edge.get_other_city(current_city)

                time_needed, fuel_consumed = self.calculate_edge_time_and_fuel(edge, current_fuel)
                
                if time_needed == float('inf'):
                    continue 

                new_fuel = current_fuel - fuel_consumed
                new_fuel = math.floor(new_fuel)
                new_g = current_g + time_needed

                new_refuel_count = refuel_count
                if next_city.has_fuel and new_fuel < self.plane.tank_capacity:
                    new_g += 0.5
                    new_fuel = self.plane.tank_capacity
                    new_refuel_count += 1

                visited_key = (next_city, new_fuel)
                if visited_key in visited and visited[visited_key] <= new_g:
                    continue
                
                visited[visited_key] = new_g
                
                h_score = self.haversine_distance(next_city, target_city) / self.plane.cruise_speed
                f_score = new_g + h_score
                
                new_path = current_path + [next_city]
                heapq.heappush(open_set, (f_score, new_g, next_city, new_fuel, new_path, new_refuel_count))
        
        return {"error": "No path found"}
    
    def _build_result(self, path: list[City], total_time: float, refuel_count: int) -> dict:
        total_distance = 0
        for i in range(len(path) - 1):
            city1, city2 = path[i], path[i + 1]
            for edge in self.graph.edges:
                if (edge.city1 == city1 and edge.city2 == city2) or (edge.city1 == city2 and edge.city2 == city1):
                    total_distance += edge.distance_km
                    break
        
        refuel_cities = []
        for i, city in enumerate(path[:-1]):
            if city.has_fuel:
                refuel_cities.append(city.name)
        
        return {
            "route": [city.name for city in path],
            "total_time": round(total_time, 2),
            "refuel_stops": refuel_cities,
            "total_distance": round(total_distance),
            "refuel_count": refuel_count
        }

def create_test_graph():
    graph = Graph()
    
    moscow = City("Moscow", 55.7558, 37.6173, has_fuel=True)
    spb = City("St Petersburg", 59.9343, 30.3351, has_fuel=True)
    kazan = City("Kazan", 55.8304, 49.0661, has_fuel=True)
    sochi = City("Sochi", 43.5855, 39.7231, has_fuel=False)
    samara = City("Samara", 53.1959, 50.1002, has_fuel=True)
    
    graph.add_city(moscow)
    graph.add_city(spb)
    graph.add_city(kazan)
    graph.add_city(sochi)
    graph.add_city(samara)
    
    graph.add_edge(Edge(moscow, spb, 650, fairwind=True))
    graph.add_edge(Edge(moscow, kazan, 720))
    graph.add_edge(Edge(moscow, sochi, 1360, headwind=True))
    graph.add_edge(Edge(kazan, samara, 450))
    graph.add_edge(Edge(spb, kazan, 1150, closed=True))
    graph.add_edge(Edge(samara, sochi, 1250))
    
    return graph

def main():
    plane = Plane(
        tank_capacity=16000,
        fuel_consumption=2.7,
        cruise_speed=841
    )
    graph = create_test_graph()
    
    planner = RoutePlanner(graph, plane)
    
    result = planner.a_star_search("Moscow", "Sochi")
    
    if "error" in result:
        print(f"Ошибка: {result['error']}")
    else:
        print(f"Маршрут: {' -> '.join(result['route'])}")
        print(f"Общее время: {result['total_time']} часов")
        print(f"Общее расстояние: {result['total_distance']} км")
        print(f"Количество дозаправок: {result['refuel_count']}")
        if result['refuel_stops']:
            print(f"Города с дозаправкой: {', '.join(result['refuel_stops'])}")
        
        total_fuel_used = 0
        for i in range(len(result['route']) - 1):
            city1_name, city2_name = result['route'][i], result['route'][i + 1]
            city1 = graph.cities[city1_name]
            city2 = graph.cities[city2_name]
            
            for edge in graph.edges:
                if (edge.city1.name == city1_name and edge.city2.name == city2_name) or \
                   (edge.city1.name == city2_name and edge.city2.name == city1_name):
                    
                    time_needed, fuel_used = planner.calculate_edge_time_and_fuel(edge, plane.tank_capacity)
                    total_fuel_used += fuel_used
                    
                    print(f"{city1_name} -> {city2_name}: {time_needed} ч, расход {fuel_used} л")
                    
                    if city2.has_fuel and i < len(result['route']) - 2:
                        print(f"  [Дозаправка в {city2_name}] +0.5 ч")
                    break

if __name__ == "__main__":
    main()