import math
import heapq
class Sensor:
    def __init__(self, name: str, x: float, y: float, sensor_class: str):
        self.name = name
        self.x = x
        self.y = y
        self.sensor_class = sensor_class  # 'A', 'B', or 'C'   
    def __repr__(self):
        return f"Sensor({self.name}, {self.sensor_class})"
class Edge:
    def __init__(self, sensor1: Sensor, sensor2: Sensor, distance: float):
        self.sensor1 = sensor1
        self.sensor2 = sensor2
        self.distance = distance
        self.cost = self.calculate_cost()
    def calculate_cost(self) -> float:
        distance_meters = self.distance * 5000
        if self.sensor1.sensor_class == 'C' or self.sensor2.sensor_class == 'C':
            cost_per_100m = 1000
        elif self.sensor1.sensor_class == 'B' or self.sensor2.sensor_class == 'B':
            cost_per_100m = 900
        else:
            cost_per_100m = 750
        return (distance_meters / 100) * cost_per_100m  
    def __repr__(self):
        return f"Edge({self.sensor1.name} - {self.sensor2.name}: {self.cost:.2f} руб)"
class DataCenter:
    def __init__(self, sensor: Sensor, radius: float):
        self.sensor = sensor
        self.radius = radius
        self.covered_sensors: list[Sensor] = [sensor] 
    def add_sensor(self, sensor: Sensor):
        self.covered_sensors.append(sensor) 
    def __repr__(self):
        return f"DataCenter({self.sensor.name}, радиус: {self.radius})"
class SpanningTree:
    def __init__(self, data_center: DataCenter):
        self.data_center = data_center
        self.edges: list[Edge] = []
        self.total_cost = 0.0
        self.total_traffic = 0.0 
    def add_edge(self, edge: Edge):
        self.edges.append(edge)
        self.total_cost += edge.cost
        for sensor in [edge.sensor1, edge.sensor2]:
            if sensor.sensor_class == 'C':
                self.total_traffic += 250
            elif sensor.sensor_class == 'B':
                self.total_traffic += 170
            else:  # Class A
                self.total_traffic += 150 
    def __repr__(self):
        return f"SpanningTree(Центр: {self.data_center.sensor.name}, Стоимость: {self.total_cost:.2f} руб)"
class SensorNetwork:
    def __init__(self):
        self.sensors: list[Sensor] = []
        self.edges: list[Edge] = []
    def add_sensor(self, sensor: Sensor):
        self.sensors.append(sensor)
    def calculate_distance(self, sensor1: Sensor, sensor2: Sensor) -> float:
        dx = sensor1.x - sensor2.x
        dy = sensor1.y - sensor2.y
        return math.sqrt(dx*dx + dy*dy)
    def create_edges(self):
        self.edges = []
        n = len(self.sensors)
        for i in range(n):
            for j in range(i + 1, n):
                distance = self.calculate_distance(self.sensors[i], self.sensors[j])
                edge = Edge(self.sensors[i], self.sensors[j], distance)
                self.edges.append(edge)
    def find_data_centers(self, radius: float) -> list[DataCenter]:
        uncovered_sensors = set(self.sensors)
        data_centers = [] 
        while uncovered_sensors:
            best_center = None
            best_coverage = 0
            for sensor in list(uncovered_sensors):
                coverage_count = 0
                for other_sensor in uncovered_sensors:
                    distance = self.calculate_distance(sensor, other_sensor)
                    if distance <= radius:
                        coverage_count += 1         
                if coverage_count > best_coverage:
                    best_coverage = coverage_count
                    best_center = sensor     
            if best_center is None:
                break
            data_center = DataCenter(best_center, radius)
            for sensor in list(uncovered_sensors):
                distance = self.calculate_distance(best_center, sensor)
                if distance <= radius:
                    data_center.add_sensor(sensor)
                    uncovered_sensors.remove(sensor)   
            data_centers.append(data_center)
        return data_centers
    def prim_algorithm(self, sensors: list[Sensor]) -> SpanningTree:
        if not sensors:
            return None
        data_center = DataCenter(sensors[0], 0)
        spanning_tree = SpanningTree(data_center)
        visited = set([sensors[0]])
        available_edges = []
        for edge in self.edges:
            if (edge.sensor1 in sensors and edge.sensor2 in sensors and
                (edge.sensor1 in visited or edge.sensor2 in visited) and
                not (edge.sensor1 in visited and edge.sensor2 in visited)):
                heapq.heappush(available_edges, (edge.cost, edge))
        while len(visited) < len(sensors) and available_edges:
            cost, edge = heapq.heappop(available_edges)
            new_sensor = None
            if edge.sensor1 in visited and edge.sensor2 not in visited:
                new_sensor = edge.sensor2
            elif edge.sensor2 in visited and edge.sensor1 not in visited:
                new_sensor = edge.sensor1  
            if new_sensor and new_sensor in sensors:
                spanning_tree.add_edge(edge)
                visited.add(new_sensor)
                for new_edge in self.edges:
                    if (new_edge.sensor1 in sensors and new_edge.sensor2 in sensors and
                        (new_edge.sensor1 == new_sensor or new_edge.sensor2 == new_sensor) and
                        not (new_edge.sensor1 in visited and new_edge.sensor2 in visited)):
                        heapq.heappush(available_edges, (new_edge.cost, new_edge))
        return spanning_tree
    def create_spanning_forest(self, radius: float) -> list[SpanningTree]:
        self.create_edges()
        data_centers = self.find_data_centers(radius)
        spanning_trees = []
        for data_center in data_centers:
            spanning_tree = self.prim_algorithm(data_center.covered_sensors)
            if spanning_tree:
                spanning_trees.append(spanning_tree)
        return spanning_trees
def create_test_network():
    network = SensorNetwork()
    sensors_data = [
        ("S1", 1.0, 1.0, "A"),
        ("S2", 2.0, 1.5, "B"),
        ("S3", 3.0, 2.0, "C"),
        ("S4", 1.5, 3.0, "A"),
        ("S5", 2.5, 3.5, "B"),
        ("S6", 4.0, 1.0, "C"),
        ("S7", 4.5, 3.0, "A"),
        ("S8", 3.5, 4.0, "B"),
    ]
    for name, x, y, sensor_class in sensors_data:
        network.add_sensor(Sensor(name, x, y, sensor_class))
    return network
def main():
    network = create_test_network()
    try:
        radius = float(input("Введите радиус охвата центров сбора (в единицах координат): "))
    except ValueError:
        print("Ошибка: введите числовое значение")
        return
    print(f"Радиус охвата: {radius}")
    print(f"Всего датчиков: {len(network.sensors)}")
    spanning_forest = network.create_spanning_forest(radius)
    total_centers = len(spanning_forest)
    total_cost = 0.0
    for i, tree in enumerate(spanning_forest, 1):
        center = tree.data_center
        print(f"\nЦентр {i}: {center.sensor.name}")
        print(f"  Охватывает датчики: {[s.name for s in center.covered_sensors]}")
        print(f"  Количество датчиков: {len(center.covered_sensors)}")
        print(f"  Центр: {tree.data_center.sensor.name}")
        print(f"  Стоимость подключения: {tree.total_cost:.2f} руб")
        print(f"  Суммарный трафик: {tree.total_traffic:.0f} Mbit")
        if tree.total_traffic > 1000:
            print(f"ПРЕДУПРЕЖДЕНИЕ: Превышен лимит трафика") 
        for edge in tree.edges:
            distance_km = edge.distance * 5  
            print(f"    {edge.sensor1.name} - {edge.sensor2.name}: "
                  f"{edge.cost:.2f} руб ({distance_km:.1f} км)") 
        total_cost += tree.total_cost 
    print(f"Всего центров сбора: {total_centers}")
    print(f"Общая стоимость: {total_cost:.2f} руб")
    all_sensors_covered = sum(len(tree.data_center.covered_sensors) for tree in spanning_forest)
    print(f"Охвачено датчиков: {all_sensors_covered} из {len(network.sensors)}")
    if all_sensors_covered < len(network.sensors):
        print("Не все датчики охвачены! Увеличьте радиус.")
if __name__ == "__main__":
    main()