from typing import Any, List, Optional, Dict, Set
from enum import Enum
import time
import random

class StationType(Enum):
    REGULAR = "regular"      # Normal station
    JUNCTION = "junction"    # Junction point (multiple lines)
    TERMINAL = "terminal"    # End of line
    EXPRESS = "express"      # Express stop
    TRANSFER = "transfer"    # Transfer hub

class TrackType(Enum):
    MAIN = "main"           # Main line
    BRANCH = "branch"       # Branch line  
    EXPRESS = "express"     # Express line
    LOOP = "loop"          # Loop line

class SubwayStation:
    """Subway station-like data node"""
    def __init__(self, station_id: str, data: Any, station_type: StationType = StationType.REGULAR):
        self.station_id = station_id
        self.data = data
        self.station_type = station_type
        
        # Subway connections - Metro-like connections
        self.next_stations = {}  # track_type -> next_station
        self.prev_stations = {}  # track_type -> prev_station
        self.branch_connections = []  # Branch line connections
        self.express_skip_to = None  # Express skip connection
        self.transfer_destinations = []  # Transfer destinations
        
        # Metro-specific properties
        self.line_colors = set()  # Lines passing through this station
        self.passenger_capacity = 1  # How much data it can hold
        self.access_frequency = 0  # How often it's accessed
        self.is_active = True
        
        # Performance tracking
        self.last_accessed = None
        self.access_pattern = []  # Recent access types

class SubwayTrack:
    """Subway line-like data pathway"""
    def __init__(self, track_id: str, track_type: TrackType, color: str):
        self.track_id = track_id
        self.track_type = track_type
        self.color = color
        self.stations = []  # Stations on this track (ordered)
        self.is_bidirectional = True
        self.express_stops = set()  # Stations where express stops
        self.capacity = float('inf')  # Track capacity

class SubwayNetwork:
    """
    Subway network-like data structure
    
    Core Principles:
    1. Data is stored in stations
    2. Organized over tracks  
    3. Branching/transfers at junctions
    4. Express lines for long-distance optimization
    5. Special structure for terminal loops
    """
    
    def __init__(self):
        self.stations = {}  # station_id -> SubwayStation
        self.tracks = {}    # track_id -> SubwayTrack
        self.junctions = {}  # junction_id -> set of connected tracks
        self.network_map = {}  # Network topology
        
        # Performance metrics
        self.total_data_items = 0
        self.average_path_length = 0
        self.cache_efficiency = 0
        
    def create_main_line(self, line_id: str, stations_data: List[Any], color: str = "blue"):
        """Create main line (linear linked list-like)"""
        track = SubwayTrack(line_id, TrackType.MAIN, color)
        
        prev_station = None
        for i, data in enumerate(stations_data):
            station_id = f"{line_id}_station_{i}"
            station_type = StationType.TERMINAL if (i == 0 or i == len(stations_data)-1) else StationType.REGULAR
            
            station = SubwayStation(station_id, data, station_type)
            station.line_colors.add(color)
            
            # Setup linear connections
            if prev_station:
                station.prev_stations[TrackType.MAIN] = prev_station
                prev_station.next_stations[TrackType.MAIN] = station
            
            self.stations[station_id] = station
            track.stations.append(station)
            prev_station = station
        
        self.tracks[line_id] = track
        self.total_data_items += len(stations_data)
        
        return track
    
    def create_branch_line(self, branch_id: str, junction_station_id: str, 
                          branch_data: List[Any], color: str = "green"):
        """Create branch line (starting from junction)"""
        if junction_station_id not in self.stations:
            raise ValueError(f"Junction station {junction_station_id} not found")
        
        junction_station = self.stations[junction_station_id]
        junction_station.station_type = StationType.JUNCTION
        
        track = SubwayTrack(branch_id, TrackType.BRANCH, color)
        
        prev_station = junction_station
        for i, data in enumerate(branch_data):
            station_id = f"{branch_id}_station_{i}"
            station_type = StationType.TERMINAL if i == len(branch_data)-1 else StationType.REGULAR
            
            station = SubwayStation(station_id, data, station_type)
            station.line_colors.add(color)
            
            # Branch connection
            station.prev_stations[TrackType.BRANCH] = prev_station
            prev_station.next_stations[TrackType.BRANCH] = station
            
            # Junction to branch connection
            if i == 0:  # First branch station
                junction_station.branch_connections.append(station)
            
            self.stations[station_id] = station
            track.stations.append(station)
            prev_station = station
        
        self.tracks[branch_id] = track
        self.total_data_items += len(branch_data)
        
        return track
    
    def create_express_line(self, express_id: str, main_line_id: str, 
                           express_stations: List[int], color: str = "red"):
        """Create express line (connects specific stations on main line)"""
        if main_line_id not in self.tracks:
            raise ValueError(f"Main line {main_line_id} not found")
        
        main_track = self.tracks[main_line_id]
        express_track = SubwayTrack(express_id, TrackType.EXPRESS, color)
        
        prev_express_station = None
        for station_index in express_stations:
            if station_index >= len(main_track.stations):
                continue
                
            station = main_track.stations[station_index]
            station.station_type = StationType.EXPRESS
            station.line_colors.add(color)
            
            # Express connections
            if prev_express_station:
                station.prev_stations[TrackType.EXPRESS] = prev_express_station
                prev_express_station.next_stations[TrackType.EXPRESS] = station
                prev_express_station.express_skip_to = station
            
            express_track.stations.append(station)
            express_track.express_stops.add(station.station_id)
            prev_express_station = station
        
        self.tracks[express_id] = express_track
        return express_track
    
    def create_loop_connection(self, start_station_id: str, end_station_id: str, 
                              color: str = "yellow"):
        """Create terminal loop (U-shape connection)"""
        start_station = self.stations.get(start_station_id)
        end_station = self.stations.get(end_station_id)
        
        if not (start_station and end_station):
            raise ValueError("Start or end station not found for loop")
        
        loop_id = f"loop_{start_station_id}_{end_station_id}"
        loop_track = SubwayTrack(loop_id, TrackType.LOOP, color)
        
        # U-shape connection
        start_station.next_stations[TrackType.LOOP] = end_station
        end_station.prev_stations[TrackType.LOOP] = start_station
        
        start_station.line_colors.add(color)
        end_station.line_colors.add(color)
        
        loop_track.stations = [start_station, end_station]
        self.tracks[loop_id] = loop_track
        
        return loop_track
    
    def add_transfer_connection(self, station1_id: str, station2_id: str, transfer_cost: int = 1):
        """Add transfer connection between two stations"""
        station1 = self.stations.get(station1_id)
        station2 = self.stations.get(station2_id)
        
        if station1 and station2:
            station1.transfer_destinations.append((station2, transfer_cost))
            station2.transfer_destinations.append((station1, transfer_cost))
            
            station1.station_type = StationType.TRANSFER
            station2.station_type = StationType.TRANSFER
    
    def find_optimal_route(self, start_data: Any, end_data: Any) -> List[str]:
        """Metro routing-like optimal pathfinding"""
        start_station = self._find_station_by_data(start_data)
        end_station = self._find_station_by_data(end_data)
        
        if not (start_station and end_station):
            return []
        
        # Subway-specific pathfinding
        visited = set()
        queue = [(start_station, [start_station.station_id], 0)]  # station, path, cost
        
        while queue:
            current, path, cost = queue.pop(0)
            
            if current.station_id in visited:
                continue
            visited.add(current.station_id)
            
            if current == end_station:
                return path
            
            # Metro-like navigation options
            next_options = []
            
            # 1. Continue on Main/Branch line
            for track_type, next_station in current.next_stations.items():
                if next_station and next_station.station_id not in visited:
                    next_cost = cost + 1
                    if track_type == TrackType.EXPRESS:
                        next_cost = cost + 0.5  # Express is faster
                    next_options.append((next_station, path + [next_station.station_id], next_cost))
            
            # 2. Use express skip
            if current.express_skip_to and current.express_skip_to.station_id not in visited:
                next_options.append((current.express_skip_to, 
                                   path + [current.express_skip_to.station_id], cost + 0.3))
            
            # 3. Branch connections
            for branch_station in current.branch_connections:
                if branch_station.station_id not in visited:
                    next_options.append((branch_station, 
                                       path + [branch_station.station_id], cost + 1))
            
            # 4. Transfer connections
            for transfer_station, transfer_cost in current.transfer_destinations:
                if transfer_station.station_id not in visited:
                    next_options.append((transfer_station, 
                                       path + [transfer_station.station_id], 
                                       cost + transfer_cost))
            
            # 5. Loop connections
            if TrackType.LOOP in current.next_stations:
                loop_station = current.next_stations[TrackType.LOOP]
                if loop_station and loop_station.station_id not in visited:
                    next_options.append((loop_station, 
                                       path + [loop_station.station_id], cost + 2))
            
            # Sort by cost (greedy approach)
            next_options.sort(key=lambda x: x[2])
            queue.extend(next_options)
        
        return []  # No path found
    
    def _find_station_by_data(self, data: Any) -> Optional[SubwayStation]:
        """Find station by data content"""
        for station in self.stations.values():
            if station.data == data:
                return station
        return None
    
    def insert_data_optimally(self, data: Any, preferred_line: str = None) -> str:
        """Insert data at optimal location"""
        # Metro logic: Add to least busy line
        target_track = None
        
        if preferred_line and preferred_line in self.tracks:
            target_track = self.tracks[preferred_line]
        else:
            # Find least busy line
            min_load = float('inf')
            for track in self.tracks.values():
                if track.track_type in [TrackType.MAIN, TrackType.BRANCH]:
                    load = len(track.stations)
                    if load < min_load:
                        min_load = load
                        target_track = track
        
        if not target_track:
            # Create first line
            return self.create_main_line("main_0", [data]).track_id
        
        # Create new station
        station_id = f"{target_track.track_id}_auto_{len(target_track.stations)}"
        new_station = SubwayStation(station_id, data)
        new_station.line_colors.add(target_track.color)
        
        # Add to end of line
        if target_track.stations:
            last_station = target_track.stations[-1]
            last_station.next_stations[target_track.track_type] = new_station
            new_station.prev_stations[target_track.track_type] = last_station
            
            # Update terminal status
            if last_station.station_type == StationType.TERMINAL:
                last_station.station_type = StationType.REGULAR
            new_station.station_type = StationType.TERMINAL
        
        target_track.stations.append(new_station)
        self.stations[station_id] = new_station
        self.total_data_items += 1
        
        return station_id
    
    def get_network_statistics(self) -> Dict:
        """Network statistics - metro-like metrics"""
        stats = {
            'total_stations': len(self.stations),
            'total_tracks': len(self.tracks),
            'total_data_items': self.total_data_items,
            'junction_count': sum(1 for s in self.stations.values() 
                                if s.station_type == StationType.JUNCTION),
            'express_stations': sum(1 for s in self.stations.values() 
                                  if s.station_type == StationType.EXPRESS),
            'transfer_hubs': sum(1 for s in self.stations.values() 
                               if s.station_type == StationType.TRANSFER),
            'terminal_points': sum(1 for s in self.stations.values() 
                                 if s.station_type == StationType.TERMINAL),
        }
        
        # Track type distribution
        track_types = {}
        for track in self.tracks.values():
            track_types[track.track_type.value] = track_types.get(track.track_type.value, 0) + 1
        stats['track_distribution'] = track_types
        
        # Average connectivity
        total_connections = sum(len(s.next_stations) + len(s.prev_stations) + 
                              len(s.branch_connections) + len(s.transfer_destinations)
                              for s in self.stations.values())
        stats['avg_connectivity'] = total_connections / len(self.stations) if self.stations else 0
        
        return stats
    
    def visualize_network_structure(self) -> str:
        """Visualize network structure as text"""
        result = ["=== SUBWAY NETWORK STRUCTURE ===\n"]
        
        for track_id, track in self.tracks.items():
            result.append(f"🚇 {track.track_type.value.upper()} LINE: {track_id} ({track.color})")
            
            station_line = ""
            for i, station in enumerate(track.stations):
                # Station symbol based on type
                symbol = {
                    StationType.TERMINAL: "🔚",
                    StationType.JUNCTION: "🔀", 
                    StationType.EXPRESS: "⚡",
                    StationType.TRANSFER: "🔄",
                    StationType.REGULAR: "🚉"
                }[station.station_type]
                
                station_line += f"{symbol}{station.station_id}"
                if i < len(track.stations) - 1:
                    connection_type = "═══" if track.track_type == TrackType.EXPRESS else "───"
                    station_line += f"{connection_type}"
            
            result.append(f"  {station_line}")
            result.append("")
        
        return "\n".join(result)


def build_ankara_metro_network():
    """Gerçek Ankara Metro hattını temsil eden veri yapısını kurar"""
    network = SubwayNetwork()

    # M1 Hattı (Kızılay - Ostim)
    m1_data = ["Kızılay", "Sıhhiye", "Ulus", "Akköprü", "İvedik", "Ostim"]
    network.create_main_line("M1_Line", m1_data, "blue")

    # M2 Hattı (Kızılay - Çayyolu)
    m2_data = ["Kavaklıdere", "Bilkent", "Çayyolu"]
    network.create_branch_line("M2_Branch", "M1_Line_station_0", m2_data, "green")

    # M3 Hattı (Ostim'den Törekent'e uzanan dal)
    m3_data = ["Batıkent", "Törekent"]
    network.create_branch_line("M3_Branch", "M1_Line_station_5", m3_data, "red")

    # Kızılay ↔ Ostim arası ekspres hat
    network.create_express_line("Express_Line", "M1_Line", [0, 5], "yellow")

    # Çayyolu ↔ Törekent bağlantısı (halka)
    network.create_loop_connection("M2_Branch_station_2", "M3_Branch_station_1", "orange")

    # Transfer noktaları
    network.add_transfer_connection("M1_Line_station_0", "M2_Branch_station_0")
    network.add_transfer_connection("M1_Line_station_5", "M3_Branch_station_0")

    return network


def benchmark_subway_vs_traditional():
    """Subway Data Structure vs traditional structures"""
    print("=== SUBWAY DATA STRUCTURE BENCHMARK ===")
    
    # Test data
    test_data = [f"data_item_{i}" for i in range(1000)]
    
    # Subway Network
    start_time = time.time()
    subway = SubwayNetwork()
    
    # Create initial main line
    subway.create_main_line("main_0", test_data[:100], "blue")
    
    # Sequential insertion with safe branch creation
    for i, data in enumerate(test_data[100:], 100):
        if i % 100 == 0 and i > 0:
            # Create branch every 100 items - choose safe junction
            available_stations = list(subway.stations.keys())
            if available_stations:
                # Make station with least connections a junction
                junction_station = min(available_stations, 
                                     key=lambda x: len(subway.stations[x].branch_connections))
                try:
                    subway.create_branch_line(f"branch_{i//100}", 
                                             junction_station, 
                                             test_data[i:i+min(50, len(test_data)-i)],
                                             f"color_{i//100}")
                except ValueError:
                    # If junction not found, do normal insertion
                    subway.insert_data_optimally(data)
        else:
            subway.insert_data_optimally(data)
    
    subway_build_time = time.time() - start_time
    
    # Traditional List
    start_time = time.time()
    traditional_list = []
    traditional_list.extend(test_data)
    list_build_time = time.time() - start_time
    
    # Route finding test
    start_time = time.time()
    routes_found = 0
    for i in range(100):
        start_data = test_data[random.randint(0, len(test_data)//2)]
        end_data = test_data[random.randint(len(test_data)//2, len(test_data)-1)]
        route = subway.find_optimal_route(start_data, end_data)
        if route:
            routes_found += 1
    subway_route_time = time.time() - start_time
    
    # Traditional search
    start_time = time.time()
    searches_found = 0
    for i in range(100):
        start_data = test_data[random.randint(0, len(test_data)//2)]
        end_data = test_data[random.randint(len(test_data)//2, len(test_data)-1)]
        if start_data in traditional_list and end_data in traditional_list:
            searches_found += 1
    list_search_time = time.time() - start_time
    
    print(f"Build Time - Subway: {subway_build_time:.4f}s, List: {list_build_time:.4f}s")
    print(f"Route/Search Time - Subway: {subway_route_time:.4f}s, List: {list_search_time:.4f}s")
    print(f"Routes Found: {routes_found}/100, Searches: {searches_found}/100")
    
    # Network statistics
    stats = subway.get_network_statistics()
    print(f"\nSubway Network Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    return subway


if __name__ == "__main__":
    # Ankara Metro ağını oluştur
    ankara_network = build_ankara_metro_network()

    # Ağ yapısını göster
    print(ankara_network.visualize_network_structure())

    # İstatistikler
    stats = ankara_network.get_network_statistics()
    print("Network Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Rota testi
    print("\n=== ROTA TESTİ ===")
    route_ids = ankara_network.find_optimal_route("Bilkent", "Törekent")
    route_names = [ankara_network.stations[s].data for s in route_ids]
    print(f"Bilkent'ten Törekent'e rota: {' -> '.join(route_names)}")

    # Performans karşılaştırması
    print("\n" + "="*50)
    benchmark_subway_vs_traditional()
