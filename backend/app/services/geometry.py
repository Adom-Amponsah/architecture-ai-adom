import trimesh
import numpy as np
from typing import List, Dict, Any
import io

class GeometryService:
    def create_3d_model(self, rooms_geometry: List[Dict[str, Any]], height_meters: float = 3.0) -> bytes:
        """
        Extrudes 2D room geometry into a 3D GLB model.
        """
        scene = trimesh.Scene()
        
        # Floor base
        # We can calculate bounds to create a floor or just let rooms be floors
        
        for room in rooms_geometry:
            # Create floor mesh
            # Scale down: The SVG coords are in pixels (e.g. 400, 300).
            # We should scale them to meters for 3D. 
            # Let's say 100 pixels = 1 meter for simplicity in this MVP visualization.
            
            scale_factor = 0.02 # 100px -> 2m, 50px -> 1m. Roughly.
            
            w = room['width'] * scale_factor
            d = room['height'] * scale_factor # Depth in 3D (Z or Y)
            x = room['center_x'] * scale_factor
            z = room['center_y'] * scale_factor # Map 2D Y to 3D Z (top-down view)
            
            # Floor Box
            # trimesh.creation.box(extents) centers at origin
            floor_box = trimesh.creation.box(extents=[w, 0.2, d])
            
            # Move to position
            # Y is up. Floor is at Y=0.
            translation = [x, 0.1, z] 
            floor_box.apply_translation(translation)
            
            # Color based on room type
            color = self._get_room_color_rgba(room['type'])
            floor_box.visual.face_colors = color
            
            scene.add_geometry(floor_box)
            
            # Walls (Procedural)
            # Create 4 walls
            wall_thickness = 0.2
            wall_height = height_meters
            
            # Extents: [x, y, z]
            
            # North/South Walls (along X axis)
            wall_ns_extents = [w + wall_thickness*2, wall_height, wall_thickness]
            
            wall_n = trimesh.creation.box(extents=wall_ns_extents)
            wall_n.apply_translation([x, wall_height/2, z - d/2 - wall_thickness/2])
            wall_n.visual.face_colors = [200, 200, 200, 255]
            scene.add_geometry(wall_n)

            wall_s = trimesh.creation.box(extents=wall_ns_extents)
            wall_s.apply_translation([x, wall_height/2, z + d/2 + wall_thickness/2])
            wall_s.visual.face_colors = [200, 200, 200, 255]
            scene.add_geometry(wall_s)
            
            # East/West Walls (along Z axis)
            wall_ew_extents = [wall_thickness, wall_height, d]
            
            wall_e = trimesh.creation.box(extents=wall_ew_extents)
            wall_e.apply_translation([x + w/2 + wall_thickness/2, wall_height/2, z])
            wall_e.visual.face_colors = [200, 200, 200, 255]
            scene.add_geometry(wall_e)
            
            wall_w = trimesh.creation.box(extents=wall_ew_extents)
            wall_w.apply_translation([x - w/2 - wall_thickness/2, wall_height/2, z])
            wall_w.visual.face_colors = [200, 200, 200, 255]
            scene.add_geometry(wall_w)
            
        # Export to GLB
        glb_data = scene.export(file_type='glb')
        return glb_data

    def _get_room_color_rgba(self, room_type: str) -> List[int]:
        # RGB + Alpha
        colors = {
            "living_room": [255, 204, 128, 255], # Orange
            "kitchen": [239, 154, 154, 255],    # Red
            "bedroom": [144, 202, 249, 255],    # Blue
            "bathroom": [129, 199, 132, 255],   # Green
            "balcony": [176, 190, 197, 255],    # Grey
            "entrance": [255, 245, 157, 255],   # Yellow
            "corridor": [224, 224, 224, 255],
            "other": [206, 147, 216, 255]       # Purple
        }
        return colors.get(room_type, [200, 200, 200, 255])

geometry_service = GeometryService()
