import math
import heapq
from typing import List, Dict, Tuple, Optional

class Graph:
    def __init__(self, matrix: List[List[int]]):
        self.matrix = matrix
        self.n = len(matrix)
        self.edges = {}
        self._build_graph()
        
        self.cell_size = 10 
        self.base_speed = 10  
        
        self.speed_multipliers = {
            0: 1.0,   
            1: 0.75,  
            2: 0.5    
        }
    
    def _build_graph(self):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  
        for i in range(self.n):
            for j in range(self.n):
                if self.matrix[i][j] == -1:
                    continue
                neighbors = []
                for dx, dy in directions:
                    ni, nj = i + dx, j + dy
                    if (0 <= ni < self.n and 0 <= nj < self.n and 
                        self.matrix[ni][nj] != -1):
                        neighbors.append((ni, nj))
                self.edges[(i, j)] = neighbors
    
    def _calculate_edge_time(self, start: Tuple[int, int], end: Tuple[int, int]) -> float:
        start_type = self.matrix[start[0]][start[1]]
        end_type = self.matrix[end[0]][end[1]]
        
        start_speed = self.base_speed * self.speed_multipliers[start_type]
        end_speed = self.base_speed * self.speed_multipliers[end_type]
        
        half_distance = self.cell_size / 2
        
        time_first_half = half_distance / start_speed
        
        time_second_half = half_distance / end_speed
        
        total_time = time_first_half + time_second_half
        
        return round(total_time, 2)
    
    def calculate_path_time(self, start: Tuple[int, int], end: Tuple[int, int], 
                          return_path: bool = False) -> float:

        if (not self._is_valid_cell(start) or not self._is_valid_cell(end) or
            self.matrix[start[0]][start[1]] == -1 or 
            self.matrix[end[0]][end[1]] == -1):
            raise ValueError("Недопустимые координаты начальной или конечной точки")
        
        distances = {cell: float('inf') for cell in self.edges}
        distances[start] = 0
        previous = {cell: None for cell in self.edges}
        
        pq = [(0, start)]
        
        while pq:
            current_distance, current_cell = heapq.heappop(pq)
            
            if current_cell == end:
                break
            
            if current_distance > distances[current_cell]:
                continue
            
            for neighbor in self.edges[current_cell]:
                edge_time = self._calculate_edge_time(current_cell, neighbor)
                new_distance = current_distance + edge_time
                
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_cell
                    heapq.heappush(pq, (new_distance, neighbor))

        if distances[end] == float('inf'):
            raise ValueError("Путь между точками не существует")
        
        final_time = round(distances[end], 2)
        
        if return_path:
            self._print_path(start, end, previous, distances)
        
        return final_time
    
    def _print_path(self, start: Tuple[int, int], end: Tuple[int, int], 
                   previous: Dict, distances: Dict):
        path = []
        current = end

        while current is not None:
            path.append(current)
            current = previous[current]
        
        path.reverse()
        
        print("Найденный путь:")
        for i, cell in enumerate(path):
            time_to_cell = round(distances[cell], 2)
            cell_type = self.matrix[cell[0]][cell[1]]
            speed_percent = self.speed_multipliers[cell_type] * 100
            print(f"  {i+1}. Клетка {cell} (тип: {cell_type}, скорость: {speed_percent}%) - время: {time_to_cell}")
        
        print(f"Общее время пути: {round(distances[end], 2)}")
    
    def _is_valid_cell(self, cell: Tuple[int, int]) -> bool:
        i, j = cell
        return 0 <= i < self.n and 0 <= j < self.n


matrix = [
    [0, 1],
    [-1, 0]
] 
graph = Graph(matrix)
time2 = graph.calculate_path_time((0, 0), (1, 1), return_path=True)