#!/usr/bin/env python3

"""
Thermal Calculation Routes
API endpoints for emergency rating calculations
"""

from flask import Blueprint, request, jsonify
import numpy as np
from thermal_engine import ThermalNetwork, EmergencyRatingCalculator, RadialTemperatureCalculator
from cable_library import get_cable_library

thermal_bp = Blueprint('thermal', __name__)

# Initialize cable library
cable_lib = get_cable_library()

def get_cable_thermal_parameters(cable_type):
    """Helper function to get cable thermal parameters"""
    try:
        geometry, materials = cable_lib.get_thermal_parameters(cable_type)
        cable_data = cable_lib.get_cable_data(cable_type)
        return geometry, materials, cable_data
    except Exception as e:
        print(f"Error getting cable parameters: {e}")
        return None, None, None

@thermal_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Emergency Rating Calculator',
        'version': '1.0'
    })

@thermal_bp.route('/cable-types')
def get_cable_types():
    """Get available cable types"""
    try:
        cable_types = cable_lib.get_cable_types()
        return jsonify({'cable_types': cable_types})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@thermal_bp.route('/cable-parameters/<cable_type>')
def get_cable_parameters(cable_type):
    """Get parameters for a specific cable type"""
    try:
        cable_data = cable_lib.get_cable_data(cable_type)
        if not cable_data:
            return jsonify({'error': 'Cable type not found'}), 404
        
        # Return relevant parameters
        parameters = {
            'name': cable_data['name'],
            'description': cable_data['description'],
            'conductor_area': cable_data['conductor_area'],
            'conductor_diameter': cable_data['conductor_diameter'],
            'insulation_thickness': cable_data['insulation_thickness'],
            'max_temperature': cable_data['max_temp'],
            'conductor_material': cable_data['conductor_material'],
            'insulation_type': cable_data['insulation_type']
        }
        
        return jsonify(parameters)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@thermal_bp.route('/emergency-rating', methods=['POST'])
def calculate_emergency_rating():
    """Calculate emergency current rating"""
    data = request.get_json()
    
    try:
        # Extract parameters
        cable_type = data.get('cable_type')
        initial_current = float(data.get('initial_current', 0))
        emergency_duration = float(data.get('emergency_duration', 6))
        max_temperature = float(data.get('max_temperature', 90))
        ambient_temperature = float(data.get('ambient_temperature', 20))
        
        if not cable_type:
            return jsonify({'error': 'Cable type is required'}), 400
        
        # Get cable parameters
        geometry, materials, cable_data = get_cable_thermal_parameters(cable_type)
        
        if not geometry or not materials or not cable_data:
            return jsonify({'error': 'Unable to get cable parameters'}), 500
        
        # Create thermal network and calculator
        thermal_network = ThermalNetwork(geometry, materials)
        calculator = EmergencyRatingCalculator(thermal_network)
        
        # Get conductor area
        conductor_area = cable_data['conductor_area']
        
        # Calculate emergency rating
        emergency_current = calculator.calculate_emergency_current(
            initial_current, emergency_duration, max_temperature, 
            ambient_temperature, conductor_area
        )
        
        # Calculate initial temperature
        initial_temp = calculator.calculate_steady_state_temperature(
            initial_current, ambient_temperature, conductor_area
        )
        
        # Calculate scaling factor
        scaling_factor = emergency_current / initial_current if initial_current > 0 else 0
        
        # Check IEC compliance (≤2.5× scaling factor)
        within_iec_limit = scaling_factor <= 2.5
        
        response = {
            'emergency_current': round(emergency_current, 1),
            'initial_current': initial_current,
            'emergency_duration': emergency_duration,
            'max_temperature': max_temperature,
            'initial_temperature': round(initial_temp, 2),
            'scaling_factor': round(scaling_factor, 2),
            'within_iec_limit': within_iec_limit
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@thermal_bp.route('/steady-state-temperature', methods=['POST'])
def calculate_steady_state_temperature():
    """Calculate steady-state conductor temperature"""
    data = request.get_json()
    
    try:
        # Extract parameters
        cable_type = data.get('cable_type')
        current = float(data.get('current', 0))
        ambient_temperature = float(data.get('ambient_temperature', 20))
        
        if not cable_type:
            return jsonify({'error': 'Cable type is required'}), 400
        
        # Get cable parameters
        geometry, materials, cable_data = get_cable_thermal_parameters(cable_type)
        
        if not geometry or not materials or not cable_data:
            return jsonify({'error': 'Unable to get cable parameters'}), 500
        
        # Create thermal network and calculator
        thermal_network = ThermalNetwork(geometry, materials)
        calculator = EmergencyRatingCalculator(thermal_network)
        
        # Get conductor area
        conductor_area = cable_data['conductor_area']
        
        # Calculate temperature and losses
        conductor_temp = calculator.calculate_steady_state_temperature(
            current, ambient_temperature, conductor_area
        )
        conductor_losses = calculator.calculate_conductor_losses(
            current, conductor_temp, conductor_area
        )
        
        response = {
            'conductor_temperature': round(conductor_temp, 2),
            'temperature_rise': round(conductor_temp - ambient_temperature, 2),
            'conductor_losses': round(conductor_losses, 2),
            'current': current,
            'ambient_temperature': ambient_temperature
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@thermal_bp.route('/transient-analysis', methods=['POST'])
def calculate_transient_analysis():
    """Calculate transient thermal analysis"""
    data = request.get_json()
    
    try:
        # Extract parameters
        cable_type = data.get('cable_type')
        initial_current = float(data.get('initial_current', 0))
        emergency_current = float(data.get('emergency_current', 0))
        duration_hours = float(data.get('duration_hours', 6))
        ambient_temperature = float(data.get('ambient_temperature', 20))
        
        if not cable_type:
            return jsonify({'error': 'Cable type is required'}), 400
        
        # Get cable parameters
        geometry, materials, cable_data = get_cable_thermal_parameters(cable_type)
        
        if not geometry or not materials or not cable_data:
            return jsonify({'error': 'Unable to get cable parameters'}), 500
        
        # Create thermal network and calculator
        thermal_network = ThermalNetwork(geometry, materials)
        calculator = EmergencyRatingCalculator(thermal_network)
        
        # Get conductor area
        conductor_area = cable_data['conductor_area']
        
        # Calculate transient temperature profile
        time_hours, temperature_celsius = calculator.calculate_transient_temperature(
            initial_current, emergency_current, duration_hours, 
            ambient_temperature, conductor_area
        )
        
        response = {
            'time_hours': time_hours.tolist(),
            'temperature_celsius': temperature_celsius.tolist(),
            'initial_current': initial_current,
            'emergency_current': emergency_current,
            'duration_hours': duration_hours,
            'max_temperature': round(float(np.max(temperature_celsius)), 2),
            'final_temperature': round(float(temperature_celsius[-1]), 2)
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@thermal_bp.route('/radial-temperature', methods=['POST'])
def calculate_radial_temperature():
    """Calculate radial temperature distribution"""
    data = request.get_json()
    
    try:
        # Extract parameters
        cable_type = data.get('cable_type')
        current = float(data.get('current', 0))
        ambient_temperature = float(data.get('ambient_temperature', 20))
        radial_points = int(data.get('radial_points', 50))
        
        if not cable_type:
            return jsonify({'error': 'Cable type is required'}), 400
        
        # Get cable parameters
        geometry, materials, cable_data = get_cable_thermal_parameters(cable_type)
        
        if not geometry or not materials or not cable_data:
            return jsonify({'error': 'Unable to get cable parameters'}), 500
        
        # Create thermal network and calculator
        thermal_network = ThermalNetwork(geometry, materials)
        radial_calculator = RadialTemperatureCalculator(thermal_network)
        
        # Get conductor area
        conductor_area = cable_data['conductor_area']
        
        # Calculate radial temperature profile
        radius_mm, temperature_celsius = radial_calculator.calculate_radial_profile(
            current, ambient_temperature, conductor_area, radial_points
        )
        
        # Get cable boundaries
        cable_boundaries = {
            'conductor_radius': geometry.conductor_radius,
            'insulation_radius': geometry.insulation_outer_radius,
            'sheath_radius': geometry.sheath_outer_radius
        }
        
        response = {
            'radius_mm': radius_mm.tolist(),
            'temperature_celsius': temperature_celsius.tolist(),
            'current': current,
            'ambient_temperature': ambient_temperature,
            'cable_boundaries': cable_boundaries,
            'max_temperature': round(float(np.max(temperature_celsius)), 2),
            'conductor_temperature': round(float(temperature_celsius[0]), 2)
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

