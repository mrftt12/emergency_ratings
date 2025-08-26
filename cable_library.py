#!/usr/bin/env python3

"""
Cable Library - Underground Power Cable Database
Processes cable data from CSV and provides thermal parameters
"""

import pandas as pd
import numpy as np
import os
from thermal_engine import CableGeometry, MaterialProperties

class CableLibrary:
    """Cable library with thermal parameter calculation"""
    
    def __init__(self):
        self.cables = {}
        self.load_cable_data()
    
    def load_cable_data(self):
        """Load cable data from CSV file"""
        csv_path = os.path.join(os.path.dirname(__file__), 'mdi710_cable_202507252014.csv')
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_path)
            
            for index, row in df.iterrows():
                try:
                    cable_id = self.create_cable_id(row)
                    cable_data = self.process_cable_row(row)
                    if cable_data:
                        self.cables[cable_id] = cable_data
                except Exception as e:
                    print(f"Error processing cable {index}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error loading cable library: {e}")
            # Load default cables if CSV fails
            self.load_default_cables()
    
    def create_cable_id(self, row):
        """Create unique cable identifier"""
        size = str(row.get('cable_size', '')).replace(' ', '_').replace('/', '_')
        voltage = str(row.get('voltage', '')).replace(' ', '_').replace('/', '_')
        material = str(row.get('material', 'CU'))
        insulation = str(row.get('insul_material', 'XLPE'))
        
        return f"{size}_{voltage}_{material}_{insulation}"
    
    def process_cable_row(self, row):
        """Process individual cable row and calculate thermal parameters"""
        try:
            # Extract basic cable information
            cable_size = str(row.get('cable_size', ''))
            voltage = str(row.get('voltage', ''))
            material = str(row.get('material', 'CU'))
            insulation = str(row.get('insul_material', 'XLPE'))
            
            # Calculate conductor area and diameter
            conductor_area = self.calculate_conductor_area(cable_size)
            conductor_diameter = self.calculate_conductor_diameter(conductor_area)
            
            # Estimate insulation thickness based on voltage
            insulation_thickness = self.estimate_insulation_thickness(voltage)
            
            # Estimate sheath thickness
            sheath_thickness = 2.0  # mm, typical
            
            # Get temperature limits
            max_temp = self.get_temperature_limit(insulation)
            
            # Create cable data structure
            cable_data = {
                'name': f"{cable_size} {voltage} {material} {insulation}",
                'description': f"{cable_size} {material} conductor, {insulation} insulation, {voltage}",
                'cable_size': cable_size,
                'voltage': voltage,
                'conductor_material': material,
                'insulation_type': insulation,
                'conductor_area': conductor_area,
                'conductor_diameter': conductor_diameter,
                'insulation_thickness': insulation_thickness,
                'sheath_thickness': sheath_thickness,
                'max_temp': max_temp,
                'geometry': CableGeometry(conductor_diameter, insulation_thickness, sheath_thickness),
                'materials': MaterialProperties(material)
            }
            
            return cable_data
            
        except Exception as e:
            print(f"Error processing cable: {e}")
            return None
    
    def calculate_conductor_area(self, cable_size):
        """Calculate conductor area from cable size designation"""
        try:
            if 'MCM' in cable_size:
                # Extract MCM value
                mcm_str = cable_size.split()[0]
                if '/' in mcm_str:
                    # Handle AWG sizes like 4/0, 2/0, 1/0
                    awg_map = {
                        '4/0': 211.6,
                        '3/0': 167.8,
                        '2/0': 133.1,
                        '1/0': 105.6
                    }
                    mcm_value = awg_map.get(mcm_str, 105.6)
                else:
                    mcm_value = float(mcm_str)
                
                # Convert MCM to mm²
                return mcm_value * 0.5067
            else:
                # Default for non-MCM cables
                return 100.0
        except:
            return 100.0
    
    def calculate_conductor_diameter(self, area_mm2):
        """Calculate conductor diameter from area"""
        return 2 * np.sqrt(area_mm2 / np.pi)
    
    def estimate_insulation_thickness(self, voltage):
        """Estimate insulation thickness based on voltage level"""
        try:
            voltage_num = float(''.join(filter(str.isdigit, str(voltage))))
            if voltage_num <= 1:
                return 1.5  # mm
            elif voltage_num <= 5:
                return 2.5  # mm
            elif voltage_num <= 15:
                return 4.5  # mm
            elif voltage_num <= 25:
                return 6.0  # mm
            elif voltage_num <= 35:
                return 8.0  # mm
            else:
                return 10.0  # mm
        except:
            return 4.5  # mm, default
    
    def get_temperature_limit(self, insulation):
        """Get maximum operating temperature for insulation type"""
        temp_limits = {
            'XLPE': 90.0,
            'EPR': 90.0,
            'Paper': 80.0,
            'PILC': 85.0,
            'PVC': 70.0
        }
        return temp_limits.get(insulation, 90.0)
    
    def load_default_cables(self):
        """Load default cables if CSV loading fails"""
        default_cables = {
            '1000_MCM_15_KV_CU_XLPE': {
                'name': '1000 MCM 15 KV CU XLPE',
                'description': '1000 MCM CU conductor, XLPE insulation, 15 KV',
                'cable_size': '1000 MCM',
                'voltage': '15 KV',
                'conductor_material': 'CU',
                'insulation_type': 'XLPE',
                'conductor_area': 506.7,
                'conductor_diameter': 25.4,
                'insulation_thickness': 4.5,
                'sheath_thickness': 2.0,
                'max_temp': 90.0,
                'geometry': CableGeometry(25.4, 4.5, 2.0),
                'materials': MaterialProperties('CU')
            },
            '750_MCM_12_KV_CU_Paper': {
                'name': '750 MCM 12 KV CU Paper',
                'description': '750 MCM CU conductor, Paper insulation, 12 KV',
                'cable_size': '750 MCM',
                'voltage': '12 KV',
                'conductor_material': 'CU',
                'insulation_type': 'Paper',
                'conductor_area': 380.0,
                'conductor_diameter': 22.0,
                'insulation_thickness': 4.0,
                'sheath_thickness': 2.0,
                'max_temp': 80.0,
                'geometry': CableGeometry(22.0, 4.0, 2.0),
                'materials': MaterialProperties('CU')
            }
        }
        self.cables.update(default_cables)
    
    def get_cable_types(self):
        """Get list of available cable types"""
        cable_types = []
        for cable_id, cable_data in self.cables.items():
            cable_types.append({
                'id': cable_id,
                'name': cable_data['name'],
                'description': cable_data['description'],
                'voltage': cable_data['voltage'],
                'conductor_material': cable_data['conductor_material'],
                'insulation_type': cable_data['insulation_type'],
                'max_temp': cable_data['max_temp']
            })
        return cable_types
    
    def get_thermal_parameters(self, cable_id):
        """Get thermal parameters for a specific cable"""
        cable_data = self.cables.get(cable_id)
        if cable_data:
            return cable_data['geometry'], cable_data['materials']
        return None, None
    
    def get_cable_data(self, cable_id):
        """Get complete cable data"""
        return self.cables.get(cable_id)

# Global cable library instance
_cable_library = None

def get_cable_library():
    """Get the global cable library instance"""
    global _cable_library
    if _cable_library is None:
        _cable_library = CableLibrary()
    return _cable_library

