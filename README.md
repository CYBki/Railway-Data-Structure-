# Railway-Data-Structure-🚇

A data structure inspired by metro/subway systems for organizing and navigating data.

## What is this?

While riding the Ankara Metro, I realized that metro systems work like data structures:
- Stations store data
- Lines connect related data
- Express trains skip stops for faster access
- Transfer stations connect different data domains

So I built a data structure that works like a metro system.

## Key Concepts

- **Station**: A data node that holds information
- **Main Line**: Primary data pathway (like a linked list)
- **Branch Line**: Secondary paths that split from main lines
- **Express Line**: Fast connections that skip intermediate stops
- **Transfer**: Connections between different data domains

## Basic Usage

```python
from railway_data_structure import RailwayNetwork

# Create network
network = RailwayNetwork()

# Create main line with data
main_data = ["User", "Auth", "Process", "Response"]
network.create_main_line("main", main_data, "blue")

# Add branch from second station
branch_data = ["Cache", "Validate"]
network.create_branch_line("cache", "main_station_1", branch_data, "green")

# Create express connection (skip middle stations)
network.create_express_line("express", "main", [0, 3], "red")

# Find path between data points
route = network.find_optimal_route("User", "Cache")
print(route)  # Shows the path to take
```

## Real Example: Ankara Metro

The code includes a working model of Ankara's metro system:

```python
# Creates M1, M2, M3 lines with branches and transfers
ankara_metro = create_ankara_metro_inspired()

# Find route from Bilkent to Ostim
route = ankara_metro.find_optimal_route("Bilkent_Data", "Ostim_Data")
```

## When to Use This

This could be useful for:
- Data pipelines with branches and shortcuts
- Caching systems with multiple levels
- Game pathfinding with express routes
- Any system where data has metro-like relationships

## Files

- `railway_data_structure.py` - Main implementation
- Contains all classes: RailwayNetwork, RailwayStation, RailwayTrack
- Includes Ankara Metro example and benchmarks

## Running

```bash
python railway_data_structure.py
```

This will show the network structure, statistics, and run performance tests.

## Performance

- Insert: O(1) to add data to end of line
- Search: O(n) worst case, faster with express lines
- Route finding: Uses BFS with metro-specific optimizations

## The Idea

Traditional data structures are abstract. This one uses a familiar real-world metaphor (metro systems) to make data organization more intuitive. Instead of thinking about nodes and edges, you think about stations and train lines.

## Status

Experimental project exploring whether metro metaphors can make data structures easier to understand and use.
