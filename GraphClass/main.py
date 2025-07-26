
import unittests
import submission_checker

import random
import heapq
import itertools
import time

class Graph:
    def __init__(self, directed=False):
        """
        Initialize the Graph.

        Parameters:
        - directed (bool): Specifies whether the graph is directed. Default is False (undirected).

        Attributes:
        - graph (dict): A dictionary to store vertices and their adjacent vertices (with weights).
        - directed (bool): Indicates whether the graph is directed.
        """
        self.graph = {}
        self.directed = directed
    
    def add_vertex(self, vertex):
        """
        Add a vertex to the graph.

        Parameters:
        - vertex: The vertex to add. It must be hashable.

        Ensures that each vertex is represented in the graph dictionary as a key with an empty dictionary as its value.
        """
        if not isinstance(vertex, (int, str, tuple)):
            raise ValueError("Vertex must be a hashable type.")
        if vertex not in self.graph:
            self.graph[vertex] = {}
    
    def add_edge(self, src, dest, weight):
        """
        Add a weighted edge from src to dest. If the graph is undirected, also add from dest to src.

        Parameters:
        - src: The source vertex.
        - dest: The destination vertex.
        - weight: The weight of the edge.
        
        Prevents adding duplicate edges and ensures both vertices exist.
        """
        if src not in self.graph or dest not in self.graph:
            raise KeyError("Both vertices must exist in the graph.")
        if dest not in self.graph[src]:  # Check to prevent duplicate edges
            self.graph[src][dest] = weight
        if not self.directed and src not in self.graph[dest]:
            self.graph[dest][src] = weight
    
    def remove_edge(self, src, dest):
        """
        Remove an edge from src to dest. If the graph is undirected, also remove from dest to src.

        Parameters:
        - src: The source vertex.
        - dest: The destination vertex.
        """
        if src in self.graph and dest in self.graph[src]:
            del self.graph[src][dest]
        if not self.directed:
            if dest in self.graph and src in self.graph[dest]:
                del self.graph[dest][src]
    
    def remove_vertex(self, vertex):
        """
        Remove a vertex and all edges connected to it.

        Parameters:
        - vertex: The vertex to be removed.
        """
        if vertex in self.graph:
            # Remove any edges from other vertices to this one
            for adj in list(self.graph):
                if vertex in self.graph[adj]:
                    del self.graph[adj][vertex]
            # Remove the vertex entry itself
            del self.graph[vertex]
    
    def get_adjacent_vertices(self, vertex):
        """
        Get a list of vertices adjacent to the specified vertex.

        Parameters:
        - vertex: The vertex whose neighbors are to be retrieved.

        Returns:
        - List of adjacent vertices. Returns an empty list if vertex is not found.
        """
        return list(self.graph.get(vertex, {}).keys())  
    
    def tour_length(self, tour):
        """
        Calculate the length of a tour.  Handles cases where edges might be missing.

        Parameters:
        - tour: A list of vertices representing a tour. A tour ends and starts in the initial vertex. This is assumed, so you should not write the last vertice.

        Returns:
        - The total length of the tour. Returns infinity if any edge in the tour is missing.
        """
        if tour and tour[0] == tour[-1] and len(tour) > 1:
            raise ValueError("Tour should not include the return to the starting vertex.")
        total_length = 0
        for i in range(len(tour)):
            weight = self._get_edge_weight(tour[i], tour[(i + 1) % len(tour)])
            if weight == float('inf'):  # Check for missing edge
                return float('inf')  # Tour is invalid if any edge is missing
            total_length += weight
        return total_length

    def _get_edge_weight(self, src, dest):
        """
        Get the weight of the edge from src to dest.

        Parameters:
        - src: The source vertex.
        - dest: The destination vertex.

        Returns:
        - The weight of the edge. If the edge does not exist, returns infinity.
        """
        return self.graph[src].get(dest, float('inf'))
    
    def __str__(self):
        """
        Provide a string representation of the graph's adjacency list for easy printing and debugging.

        Returns:
        - A string representation of the graph dictionary.
        """
        return str(self.graph)

    def shortest_path(self, start, end):
        """
        Find the shortest path between start and end vertices using Dijkstra's algorithm.

        Parameters:
        - start: The starting vertex.
        - end: The ending vertex.

        Returns:
        - (length, path): A tuple where 'length' is the total weight of the shortest path,
          and 'path' is a list of vertices representing the path from start to end (inclusive).
          If no path exists, return (float('inf'), []).
        """
        queue = [(0, start, [start])]
        visited = set()

        while queue:
            (cost, vertex, path) = heapq.heappop(queue)
            if vertex == end:
                return (cost, path)
            if vertex in visited:
                continue
            visited.add(vertex)
            for neighbor, weight in self.graph.get(vertex, {}).items():
                if neighbor not in visited:
                    heapq.heappush(queue, (cost + weight, neighbor, path + [neighbor]))
        return (float('inf'), [])

class GraphTSPSmallGraph(Graph):
    def tsp_small_graph(self, start_vertex):
        """
        Solve the Travelling Salesman Problem for a small (~10 node) complete graph starting from a specified node.
        Required to find the optimal tour. Expect graphs with at most 10 nodes. Must run under 1 second.

        Parameters:
        start_vertex: The starting node.

        Returns:
        A tuple containing the total distance of the tour and a list of nodes representing the tour path.
        """
        vertices = list(self.graph.keys())
        n = len(vertices)
        idx_map = {v: i for i, v in enumerate(vertices)}
        start_idx = idx_map[start_vertex]

        # Build distance matrix
        dist = [[float('inf')] * n for _ in range(n)]
        for i, u in enumerate(vertices):
            for j, v in enumerate(vertices):
                if u == v:
                    dist[i][j] = 0
                else:
                    dist[i][j] = self._get_edge_weight(u, v)

        # DP table: dp[mask][i] = (cost, prev)
        dp = [[(float('inf'), -1) for _ in range(n)] for _ in range(1 << n)]
        dp[1 << start_idx][start_idx] = (0, -1)

        for mask in range(1 << n):
            for u in range(n):
                if not (mask & (1 << u)):
                    continue
                cost_u, _ = dp[mask][u]
                for v in range(n):
                    if mask & (1 << v):
                        continue
                    new_mask = mask | (1 << v)
                    new_cost = cost_u + dist[u][v]
                    if new_cost < dp[new_mask][v][0]:
                        dp[new_mask][v] = (new_cost, u)

        # Find best end (must return to start)
        min_cost = float('inf')
        last = -1
        full_mask = (1 << n) - 1
        for u in range(n):
            if u == start_idx:
                continue
            cost = dp[full_mask][u][0] + dist[u][start_idx]
            if cost < min_cost:
                min_cost = cost
                last = u

        # Reconstruct path
        path = []
        mask = full_mask
        u = last
        while u != -1:
            path.append(vertices[u])
            _, prev = dp[mask][u]
            mask ^= (1 << u)
            u = prev
        path.append(start_vertex)
        path.reverse()
        # Remove the last return to start (as per your docstring)
        return min_cost, path[:-1]

class GraphTSPLargeGraph(Graph):
    def tsp_large_graph(self, start):
        """
        Solve the Travelling Salesman Problem for a large (~1000 node) complete graph starting from a specified node.
        No requirement to find the optimal tour. Must run under 0.5 seconds and its solution must not be random.
        
        Parameters:
        start: The starting node.
        
        Returns:
        A tuple containing the total distance of the tour and a list of nodes representing the tour path.
        """
        vertices = list(self.graph.keys())
        n = len(vertices)
        if n == 0:
            return 0, []
        visited = set()
        path = [start]
        visited.add(start)
        current = start
        for _ in range(n - 1):
            # Find the nearest unvisited neighbor
            next_node = None
            min_dist = float('inf')
            for neighbor in self.graph[current]:
                if neighbor not in visited:
                    weight = self._get_edge_weight(current, neighbor)
                    if weight < min_dist:
                        min_dist = weight
                        next_node = neighbor
            if next_node is None:
                # Should not happen in a complete graph
                break
            path.append(next_node)
            visited.add(next_node)
            current = next_node
        # Return to start
        # As per docstring, do not include the final return to start in the path
        total_dist = self.tour_length(path)
        return total_dist, path

class GraphTSPMediumGraph(Graph):
    def tsp_medium_graph(self, start):
        """
        Solve the Travelling Salesman Problem for a medium (~300 node) complete graph starting from a specified node.
        Expected to perform better than tsp_large_graph. Must run under 1.5 seconds.
        
        Parameters:
        start: The starting node.
        
        Returns:
        A tuple containing the total distance of the tour and a list of nodes representing the tour path.
        """
        import time
        start_time = time.time()
        vertices = list(self.graph.keys())
        n = len(vertices)
        if n == 0:
            return 0, []
        
        # Helper: Nearest Neighbor tour
        def nearest_neighbor(start_node):
            visited = set()
            path = [start_node]
            visited.add(start_node)
            current = start_node
            for _ in range(n - 1):
                next_node = None
                min_dist = float('inf')
                for neighbor in self.graph[current]:
                    if neighbor not in visited:
                        weight = self._get_edge_weight(current, neighbor)
                        if weight < min_dist:
                            min_dist = weight
                            next_node = neighbor
                if next_node is None:
                    break
                path.append(next_node)
                visited.add(next_node)
                current = next_node
            return path
        
        # Helper: 2-opt swap
        def two_opt(path):
            best = path
            best_length = self.tour_length(best)
            n = len(best)
            improved = True
            while improved:
                improved = False
                # Check time at the start of each outer loop
                if time.time() - start_time > 1.4:
                    break
                for i in range(1, n - 2):
                    for j in range(i + 1, n):
                        if j - i == 1:
                            continue
                        # Check time more frequently
                        if time.time() - start_time > 1.4:
                            return best
                        new_path = best[:i] + best[i:j][::-1] + best[j:]
                        new_length = self.tour_length(new_path)
                        if new_length < best_length:
                            best = new_path
                            best_length = new_length
                            improved = True
                            break  # Accept first improvement (first improvement strategy)
                    if improved:
                        break
            return best
        
        # Only use the provided start node
        path = nearest_neighbor(start)
        path = two_opt(path)
        length = self.tour_length(path)
        return length, path

GraphShortestPath = Graph