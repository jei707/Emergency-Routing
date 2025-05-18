import tkinter as tk
from tkinter import messagebox, ttk
import heapq
import networkx as nx
import matplotlib.pyplot as plt

class EmergencyRouteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Emergency Route Optimizer")
        self.graph = {}
        self.root.geometry("550x450") 

        # Road Inputs
        self.edges_frame = tk.Frame(root)
        self.edges_frame.pack(pady=10)

        tk.Label(self.edges_frame, text="From:").grid(row=0, column=0, padx=(5, 2), sticky="w")
        self.from_entry = tk.Entry(self.edges_frame, width=15)
        self.from_entry.grid(row=0, column=1, padx=(0, 15))

        tk.Label(self.edges_frame, text="To:").grid(row=0, column=2, padx=(5, 2), sticky="w")
        self.to_entry = tk.Entry(self.edges_frame, width=15)
        self.to_entry.grid(row=0, column=3, padx=(0, 15))

        tk.Label(self.edges_frame, text="Distance (km):").grid(row=1, column=0, padx=(5, 2), sticky="w")
        self.distance_entry = tk.Entry(self.edges_frame, width=15)
        self.distance_entry.grid(row=1, column=1, padx=(0, 15))

        tk.Label(self.edges_frame, text="Time (min):").grid(row=1, column=2, padx=(5, 2), sticky="w")
        self.time_entry = tk.Entry(self.edges_frame, width=15)
        self.time_entry.grid(row=1, column=3, padx=(0, 15))

        tk.Label(self.edges_frame, text="Risk (1–5):").grid(row=1, column=4, padx=(5, 2), sticky="w")
        self.risk_entry = tk.Entry(self.edges_frame, width=10)
        self.risk_entry.grid(row=1, column=5)

        self.add_button = tk.Button(self.edges_frame, text="Add Road", command=self.add_edge)
        self.add_button.grid(row=2, column=0, columnspan=6, pady=(15, 5))

        # Road List
        self.list_frame = tk.Frame(root)
        self.list_frame.pack(pady=10)

        tk.Label(self.list_frame, text="Added Roads:").pack(anchor="w")

        self.road_listbox = tk.Listbox(self.list_frame, width=80, height=6)
        self.road_listbox.pack(side="left", fill="y")

        scrollbar = tk.Scrollbar(self.list_frame, orient="vertical")
        scrollbar.config(command=self.road_listbox.yview)
        scrollbar.pack(side="right", fill="y")

        self.road_listbox.config(yscrollcommand=scrollbar.set)

        # Route Inputs
        self.route_frame = tk.Frame(root)
        self.route_frame.pack(pady=10)

        tk.Label(self.route_frame, text="Start:").grid(row=0, column=0)
        self.source_entry = tk.Entry(self.route_frame, width=15)
        self.source_entry.grid(row=0, column=1)

        tk.Label(self.route_frame, text="Destination:").grid(row=0, column=2)
        self.dest_entry = tk.Entry(self.route_frame, width=15)
        self.dest_entry.grid(row=0, column=3)

        self.find_button = tk.Button(root, text="Find Optimal Route", command=self.find_route)
        self.find_button.pack(pady=5)

        self.graph_button = tk.Button(root, text="Show Graph", command=self.show_graph)
        self.graph_button.pack(pady=5)

        self.result_label = tk.Label(root, text="", fg="blue")
        self.result_label.pack(pady=10)

    def add_edge(self):
        u = self.from_entry.get().strip()
        v = self.to_entry.get().strip()

        try:
            distance = float(self.distance_entry.get().strip())
            time = float(self.time_entry.get().strip())
            risk = float(self.risk_entry.get().strip())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for all fields.")
            return

        if not u or not v:
            messagebox.showerror("Input Error", "Please enter both locations.")
            return

        # Composite cost using Weighted Sum Model
        distance_weight = 1.0
        time_weight = 0.5
        risk_weight = 5.0

        w = distance_weight * distance + time_weight * time + risk_weight * risk

        self.graph.setdefault(u, []).append((v, w))
        self.graph.setdefault(v, []).append((u, w))

        self.road_listbox.insert(tk.END,
            f"{u} ↔ {v} | Cost: {w:.2f} (D:{distance}, T:{time}, R:{risk})")

        for entry in [
            self.from_entry, self.to_entry, self.distance_entry,
            self.time_entry, self.risk_entry
        ]:
            entry.delete(0, tk.END)

    def find_route(self):
        start = self.source_entry.get().strip()
        end = self.dest_entry.get().strip()

        if start not in self.graph or end not in self.graph:
            messagebox.showerror("Error", "Start or destination not found in the graph.")
            return

        cost, path = self.dijkstra(start, end)

        if cost == float("inf"):
            self.result_label.config(text="No path found.")
        else:
            route_str = " → ".join(path)
            self.result_label.config(text=f"Optimal route: {route_str}\nTotal cost: {cost:.2f}")

    def dijkstra(self, start, end):
        queue = [(0, start, [start])]
        visited = set()

        while queue:
            (cost, node, path) = heapq.heappop(queue)
            if node in visited:
                continue
            visited.add(node)

            if node == end:
                return (cost, path)

            for neighbor, weight in self.graph.get(node, []):
                if neighbor not in visited:
                    heapq.heappush(queue, (cost + weight, neighbor, path + [neighbor]))

        return (float("inf"), [])

    def show_graph(self):
        G = nx.Graph()
        for node in self.graph:
            for neighbor, cost in self.graph[node]:
                if not G.has_edge(node, neighbor):
                    G.add_edge(node, neighbor, weight=round(cost, 2))

        pos = nx.spring_layout(G)
        edge_labels = nx.get_edge_attributes(G, 'weight')

        plt.figure(figsize=(7, 5))
        nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray',
                node_size=1500, font_size=10)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
        plt.title("Road Network Graph")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmergencyRouteApp(root)
    root.mainloop()
