#!/usr/bin/env python3

"""
Emergency Rating Calculator - Thermal Engine
IEC 60853-2 Compliant Underground Cable Thermal Analysis
"""

import numpy as np
import scipy.optimize as opt
import math

class CableGeometry:
    """Cable geometry parameters"""
    def __init__(self, conductor_diameter, insulation_thickness, sheath_thickness):
        self.conductor_diameter = conductor_diameter  # mm
        self.insulation_thickness = insulation_thickness  # mm
        self.sheath_thickness = sheath_thickness  # mm
        
        # Calculate radii
        self.conductor_radius = conductor_diameter / 2
        self.insulation_outer_radius = self.conductor_radius + insulation_thickness
        self.sheath_outer_radius = self.insulation_outer_radius + sheath_thickness

class MaterialProperties:
    """Material thermal properties"""
    def __init__(self, conductor_material='CU'):
        # Conductor properties
        if conductor_material == 'CU':
            self.conductor_resistivity = 0.0172  # ohm.mm²/m at 20°C
            self.conductor_thermal_conductivity = 400  # W/m.K
            self.conductor_density = 8960  # kg/m³
            self.conductor_specific_heat = 385  # J/kg.K
        else:  # Aluminum
            self.conductor_resistivity = 0.0282  # ohm.mm²/m at 20°C
            self.conductor_thermal_conductivity = 237  # W/m.K
            self.conductor_density = 2700  # kg/m³
            self.conductor_specific_heat = 897  # J/kg.K
        
        # Insulation properties (XLPE typical)
        self.insulation_thermal_conductivity = 0.4  # W/m.K
        self.insulation_density = 920  # kg/m³
        self.insulation_specific_heat = 2300  # J/kg.K
        
        # Sheath properties (PE typical)
        self.sheath_thermal_conductivity = 0.4  # W/m.K
        self.sheath_density = 950  # kg/m³
        self.sheath_specific_heat = 2300  # J/kg.K
        
        # Soil properties
        self.soil_thermal_conductivity = 1.0  # W/m.K
        self.soil_density = 1800  # kg/m³
        self.soil_specific_heat = 1800  # J/kg.K

class ThermalNetwork:
    """Thermal network model for cable"""
    def __init__(self, geometry, materials):
        self.geometry = geometry
        self.materials = materials
        self.calculate_thermal_resistances()
        self.calculate_thermal_capacitances()
    
    def calculate_thermal_resistances(self):
        """Calculate thermal resistances per unit length"""
        # Conductor to insulation inner surface
        self.R_ci = 0  # Negligible for solid conductor
        
        # Insulation thermal resistance (cylindrical)
        self.R_ins = (1 / (2 * np.pi * self.materials.insulation_thermal_conductivity)) * \
                     np.log(self.geometry.insulation_outer_radius / self.geometry.conductor_radius)
        
        # Sheath thermal resistance
        self.R_sheath = (1 / (2 * np.pi * self.materials.sheath_thermal_conductivity)) * \
                        np.log(self.geometry.sheath_outer_radius / self.geometry.insulation_outer_radius)
        
        # External thermal resistance (to ambient)
        # Simplified model for buried cable
        burial_depth = 1000  # mm, typical burial depth
        self.R_ext = 1 / (2 * np.pi * self.materials.soil_thermal_conductivity) * \
                     np.log(2 * burial_depth / self.geometry.sheath_outer_radius)
        
        # Total thermal resistance
        self.R_total = self.R_ci + self.R_ins + self.R_sheath + self.R_ext
    
    def calculate_thermal_capacitances(self):
        """Calculate thermal capacitances per unit length"""
        # Conductor thermal capacitance
        conductor_volume = np.pi * (self.geometry.conductor_radius ** 2)  # mm²/m
        self.C_conductor = (conductor_volume * 1e-6) * self.materials.conductor_density * \
                          self.materials.conductor_specific_heat  # J/m.K
        
        # Insulation thermal capacitance
        insulation_volume = np.pi * (self.geometry.insulation_outer_radius ** 2 - 
                                   self.geometry.conductor_radius ** 2)  # mm²/m
        self.C_insulation = (insulation_volume * 1e-6) * self.materials.insulation_density * \
                           self.materials.insulation_specific_heat  # J/m.K
        
        # Sheath thermal capacitance
        sheath_volume = np.pi * (self.geometry.sheath_outer_radius ** 2 - 
                               self.geometry.insulation_outer_radius ** 2)  # mm²/m
        self.C_sheath = (sheath_volume * 1e-6) * self.materials.sheath_density * \
                       self.materials.sheath_specific_heat  # J/m.K

class EmergencyRatingCalculator:
    """Emergency rating calculator based on IEC 60853-2"""
    def __init__(self, thermal_network):
        self.thermal_network = thermal_network
        self.temperature_coefficient = 0.00393  # 1/K for copper
    
    def calculate_conductor_resistance(self, temperature, conductor_area):
        """Calculate conductor resistance at given temperature"""
        # R(T) = R₂₀ * [1 + α(T - 20)]
        R_20 = self.thermal_network.materials.conductor_resistivity / conductor_area  # ohm/m
        return R_20 * (1 + self.temperature_coefficient * (temperature - 20))
    
    def calculate_conductor_losses(self, current, conductor_temp, conductor_area):
        """Calculate conductor losses per unit length"""
        resistance = self.calculate_conductor_resistance(conductor_temp, conductor_area)
        return current ** 2 * resistance  # W/m
    
    def calculate_steady_state_temperature(self, current, ambient_temp, conductor_area=500):
        """Calculate steady-state conductor temperature"""
        def temp_equation(conductor_temp):
            losses = self.calculate_conductor_losses(current, conductor_temp, conductor_area)
            calculated_temp = ambient_temp + losses * self.thermal_network.R_total
            return calculated_temp - conductor_temp
        
        # Solve for conductor temperature
        try:
            result = opt.fsolve(temp_equation, ambient_temp + 50)
            return float(result[0])
        except:
            # Fallback calculation
            R_20 = self.thermal_network.materials.conductor_resistivity / conductor_area
            losses_approx = current ** 2 * R_20
            return ambient_temp + losses_approx * self.thermal_network.R_total
    
    def calculate_emergency_current(self, initial_current, emergency_duration, max_temp, ambient_temp, conductor_area=500):
        """Calculate emergency current rating according to IEC 60853-2"""
        # Calculate initial steady-state temperature
        initial_temp = self.calculate_steady_state_temperature(initial_current, ambient_temp, conductor_area)
        
        # Calculate thermal time constant
        total_capacitance = (self.thermal_network.C_conductor + 
                           self.thermal_network.C_insulation + 
                           self.thermal_network.C_sheath)
        tau = total_capacitance * self.thermal_network.R_total  # seconds
        
        # Convert duration to seconds
        duration_seconds = emergency_duration * 3600
        
        # IEC 60853-2 emergency rating calculation
        # For transient heating: θ_f = θ_i + (θ_ss - θ_i) * [1 - exp(-t/τ)]
        # Rearranging for emergency current
        
        def emergency_equation(emergency_current):
            # Calculate steady-state temperature for emergency current
            emergency_ss_temp = self.calculate_steady_state_temperature(emergency_current, ambient_temp, conductor_area)
            
            # Calculate transient temperature after emergency duration
            temp_rise = (emergency_ss_temp - initial_temp) * (1 - np.exp(-duration_seconds / tau))
            final_temp = initial_temp + temp_rise
            
            return final_temp - max_temp
        
        try:
            # Solve for emergency current
            result = opt.fsolve(emergency_equation, initial_current * 1.5)
            emergency_current = float(result[0])
            
            # Ensure positive result
            if emergency_current < 0:
                emergency_current = initial_current
                
            return emergency_current
        except:
            # Fallback simplified calculation
            temp_ratio = (max_temp - ambient_temp) / (initial_temp - ambient_temp)
            return initial_current * np.sqrt(max(temp_ratio, 0.1))
    
    def calculate_transient_temperature(self, initial_current, emergency_current, duration_hours, ambient_temp, conductor_area=500, time_points=100):
        """Calculate transient temperature profile"""
        # Calculate initial and final steady-state temperatures
        initial_temp = self.calculate_steady_state_temperature(initial_current, ambient_temp, conductor_area)
        final_temp = self.calculate_steady_state_temperature(emergency_current, ambient_temp, conductor_area)
        
        # Calculate thermal time constant
        total_capacitance = (self.thermal_network.C_conductor + 
                           self.thermal_network.C_insulation + 
                           self.thermal_network.C_sheath)
        tau = total_capacitance * self.thermal_network.R_total  # seconds
        
        # Time array
        time_array = np.linspace(0, duration_hours * 3600, time_points)
        
        # Temperature array
        temp_array = initial_temp + (final_temp - initial_temp) * (1 - np.exp(-time_array / tau))
        
        return time_array / 3600, temp_array  # Return time in hours

class RadialTemperatureCalculator:
    """Calculate radial temperature distribution in cable"""
    def __init__(self, thermal_network):
        self.thermal_network = thermal_network
    
    def calculate_radial_profile(self, current, ambient_temp, conductor_area=500, radial_points=50):
        """Calculate radial temperature distribution"""
        # Calculate conductor temperature
        calculator = EmergencyRatingCalculator(self.thermal_network)
        conductor_temp = calculator.calculate_steady_state_temperature(current, ambient_temp, conductor_area)
        
        # Calculate conductor losses
        conductor_losses = calculator.calculate_conductor_losses(current, conductor_temp, conductor_area)
        
        # Radial positions
        r_conductor = self.thermal_network.geometry.conductor_radius
        r_insulation = self.thermal_network.geometry.insulation_outer_radius
        r_sheath = self.thermal_network.geometry.sheath_outer_radius
        r_max = r_sheath * 3  # Extend to 3x sheath radius
        
        radius_array = np.linspace(r_conductor, r_max, radial_points)
        temp_array = np.zeros(radial_points)
        
        for i, r in enumerate(radius_array):
            if r <= r_conductor:
                # Inside conductor (uniform temperature)
                temp_array[i] = conductor_temp
            elif r <= r_insulation:
                # Inside insulation
                thermal_resistance = (1 / (2 * np.pi * self.thermal_network.materials.insulation_thermal_conductivity)) * \
                                   np.log(r / r_conductor)
                temp_array[i] = conductor_temp - conductor_losses * thermal_resistance
            elif r <= r_sheath:
                # Inside sheath
                R_ins_total = self.thermal_network.R_ins
                thermal_resistance = R_ins_total + \
                                   (1 / (2 * np.pi * self.thermal_network.materials.sheath_thermal_conductivity)) * \
                                   np.log(r / r_insulation)
                temp_array[i] = conductor_temp - conductor_losses * thermal_resistance
            else:
                # Outside cable (soil)
                R_cable = self.thermal_network.R_ins + self.thermal_network.R_sheath
                thermal_resistance = R_cable + \
                                   (1 / (2 * np.pi * self.thermal_network.materials.soil_thermal_conductivity)) * \
                                   np.log(r / r_sheath)
                temp_array[i] = conductor_temp - conductor_losses * thermal_resistance
        
        return radius_array, temp_array

