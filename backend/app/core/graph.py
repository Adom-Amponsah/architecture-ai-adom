import networkx as nx
from typing import Dict, Any
from app.schemas.architecture import ArchitecturalProgram, Room, Adjacency, AdjacencyType

class GraphBuilderService:
    def build_constraint_graph(self, program: ArchitecturalProgram) -> Dict[str, Any]:
        """
        Converts an ArchitecturalProgram into a NetworkX graph JSON representation.
        Nodes = Rooms
        Edges = Adjacencies
        Global Attributes = Global Constraints
        """
        G = nx.Graph()
        
        # Add Global Constraints as graph attributes
        G.graph["global_constraints"] = program.global_constraints.model_dump()
        G.graph["raw_prompt"] = program.raw_prompt

        # Add Nodes (Rooms)
        for room in program.rooms:
            G.add_node(
                room.id,
                label=room.name,
                type=room.type.value,
                min_area=room.constraints.min_area,
                max_area=room.constraints.max_area,
                aspect_ratio=room.constraints.aspect_ratio,
                natural_light=room.constraints.natural_light,
                description=room.description
            )

        # Add Edges (Adjacencies)
        for adj in program.adjacencies:
            # Verify nodes exist to avoid errors
            if adj.room_id_a in G.nodes and adj.room_id_b in G.nodes:
                weight = self._get_adjacency_weight(adj.type)
                G.add_edge(
                    adj.room_id_a,
                    adj.room_id_b,
                    type=adj.type.value,
                    weight=weight,
                    description=adj.description
                )
        
        # Validate graph (basic connectivity check)
        # Note: Disconnected components are allowed in some cases (e.g. detached garage), 
        # but we might want to flag them.
        is_connected = nx.is_connected(G) if len(G.nodes) > 0 else True
        G.graph["is_connected"] = is_connected

        # Convert to node-link data for JSON serialization
        graph_data = nx.node_link_data(G)
        return graph_data

    def _get_adjacency_weight(self, adj_type: AdjacencyType) -> float:
        """
        Returns a numerical weight for the adjacency type.
        Higher weight = stronger attraction.
        """
        weights = {
            AdjacencyType.DIRECT: 1.0,
            AdjacencyType.ADJACENT: 0.8,
            AdjacencyType.NEAR: 0.5,
            AdjacencyType.FAR: -0.5 # Repulsion in force-directed layouts
        }
        return weights.get(adj_type, 0.1)

graph_builder = GraphBuilderService()
