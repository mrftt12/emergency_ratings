# Emergency Rating Calculator

## Overview
Professional web application for calculating emergency thermal ratings of underground power cables according to IEC 60853-2 standard.

## Features
- **Emergency Current Rating**: Calculate maximum permissible emergency current for specified duration
- **Conductor Temperature Analysis**: Steady-state temperature calculations
- **Transient Thermal Analysis**: Full thermal transient simulation during emergency loading  
- **Radial Temperature Distribution**: Visualize temperature profile across cable cross-section
- **Cable Library**: Integrated database of 20+ real underground power cables
- **IEC 60853-2 Compliance**: Professional-grade calculations with compliance checking

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
1. Extract the zip file to your desired location
2. Navigate to the project directory:
   ```bash
   cd emergency_rating_calculator_v1
   ```

3. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Development Mode
```bash
cd src
python main.py
```

The application will be available at: http://localhost:5000

### Production Mode
For production deployment, use a WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

## Project Structure
```
emergency_rating_calculator_v1/
├── src/
│   ├── main.py                    # Main Flask application
│   ├── thermal_engine.py          # Core thermal calculation engine
│   ├── cable_library.py           # Cable database and parameter processing
│   ├── mdi710_cable_202507252014.csv  # Cable database CSV
│   ├── routes/
│   │   └── thermal.py             # API routes for thermal calculations
│   └── static/
│       ├── index.html             # Main web interface
│       ├── styles.css             # Modern minimal styling
│       ├── app.js                 # Interactive JavaScript functionality
│       └── favicon.ico            # Application icon
├── venv/                          # Python virtual environment
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## API Endpoints

### Health Check
- **GET** `/api/thermal/health` - Service health status

### Cable Library
- **GET** `/api/thermal/cable-types` - List all available cables
- **GET** `/api/thermal/cable-parameters/{cable_type}` - Get specific cable parameters

### Thermal Calculations
- **POST** `/api/thermal/emergency-rating` - Calculate emergency current rating
- **POST** `/api/thermal/steady-state-temperature` - Calculate conductor temperature
- **POST** `/api/thermal/transient-analysis` - Transient thermal simulation
- **POST** `/api/thermal/radial-temperature` - Radial temperature distribution

## Cable Library
The application includes a comprehensive database of underground power cables:
- **20+ Real Cables** with actual specifications
- **Multiple Voltage Classes**: 12kV, 15kV, 17kV, 35kV
- **Conductor Materials**: Copper (CU) and Aluminum (AL)
- **Insulation Types**: XLPE, EPR, Paper, PILC
- **Size Range**: From 2 MCM to 1500 MCM

## Technical Implementation

### Thermal Engine
- **IEC 60853-2 Compliant**: Full implementation of international standard
- **Thermal Network Modeling**: Resistances and capacitances for transient analysis
- **Material Properties**: Temperature-dependent conductor resistance
- **Radial Heat Transfer**: Cylindrical coordinate thermal analysis

### Web Interface
- **Modern Design**: Clean, minimal professional interface
- **Responsive Layout**: Works on desktop and mobile devices
- **Interactive Charts**: Real-time visualization with Chart.js
- **Tab Navigation**: Organized interface for different analysis types

### API Architecture
- **RESTful Design**: Standard HTTP methods and status codes
- **JSON Communication**: Structured data exchange
- **Error Handling**: Comprehensive error responses
- **CORS Enabled**: Cross-origin resource sharing support

## Usage Examples

### Emergency Rating Calculation
```javascript
POST /api/thermal/emergency-rating
{
  "cable_type": "1000_MCM_15_KV_CU_XLPE",
  "initial_current": 800,
  "emergency_duration": 6,
  "max_temperature": 90,
  "ambient_temperature": 20
}
```

### Conductor Temperature Analysis
```javascript
POST /api/thermal/steady-state-temperature
{
  "cable_type": "750_MCM_12_KV_CU_Paper",
  "current": 500,
  "ambient_temperature": 20
}
```

## Compliance and Standards
- **IEC 60853-2**: Calculation of the current rating - Thermal resistance
- **Professional Grade**: Suitable for engineering analysis and design
- **Validation**: Results validated against industry standards

## Support
For technical support or questions about the thermal calculations, refer to:
- IEC 60853-2 standard documentation
- Cable manufacturer specifications
- Professional electrical engineering resources

## License
This application is provided for professional use in electrical engineering applications.

---
**Emergency Rating Calculator v1.0**  
*Professional Underground Cable Thermal Analysis*

