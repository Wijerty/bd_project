# Project Structure

This document summarizes all files in the anti-fraud P2P transfer system project.

## Database Design
- [database_design.md](file://d:\вуз\bd_project\database_design.md) - Comprehensive design document with entity descriptions and sample queries
- [schema.sql](file://d:\вуз\bd_project\schema.sql) - Complete database schema with tables, constraints, indexes, and sample data

## Application Code
- [fraud_detection.py](file://d:\вуз\bd_project\fraud_detection.py) - Python script demonstrating fraud detection algorithms
- [requirements.txt](file://d:\вуз\bd_project\requirements.txt) - Python dependencies for the fraud detection script

## Security Dashboard
- [security_dashboard/](file://d:\вуз\bd_project\security_dashboard) - Web-based dashboard for security analysts
  - [app.py](file://d:\вуз\bd_project\security_dashboard\app.py) - Flask backend application
  - [requirements.txt](file://d:\вуз\bd_project\security_dashboard\requirements.txt) - Python dependencies for the dashboard
  - [README.md](file://d:\вуз\bd_project\security_dashboard\README.md) - Dashboard documentation (in Russian)
  - [templates/](file://d:\вуз\bd_project\security_dashboard\templates) - HTML templates
    - [index.html](file://d:\вуз\bd_project\security_dashboard\templates\index.html) - Main dashboard template (in Russian)
  - [static/](file://d:\вуз\bd_project\security_dashboard\static) - Static assets
    - [css/](file://d:\вуз\bd_project\security_dashboard\static\css) - Stylesheets
      - [style.css](file://d:\вуз\bd_project\security_dashboard\static\css\style.css) - Custom styles
    - [js/](file://d:\вуз\bd_project\security_dashboard\static\js) - JavaScript files
      - [dashboard.js](file://d:\вуз\bd_project\security_dashboard\static\js\dashboard.js) - Dashboard functionality (in Russian)

## Deployment
- [Dockerfile](file://d:\вуз\bd_project\Dockerfile) - Docker configuration for the PostgreSQL database
- [docker-compose.yml](file://d:\вуз\bd_project\docker-compose.yml) - Docker Compose configuration for easy deployment
- [docker-compose-full.yml](file://d:\вуз\bd_project\docker-compose-full.yml) - Docker Compose configuration for full system deployment

## Documentation
- [README.md](file://d:\вуз\bd_project\README.md) - Project overview and description
- [SETUP.md](file://d:\вуз\bd_project\SETUP.md) - Detailed setup and usage instructions
- [PROJECT_STRUCTURE.md](file://d:\вуз\bd_project\PROJECT_STRUCTURE.md) - Summary of all files
- [SECURITY_DASHBOARD.md](file://d:\вуз\bd_project\SECURITY_DASHBOARD.md) - Security dashboard documentation

## How to Get Started

1. Review [README.md](file://d:\вуз\bd_project\README.md) for an overview of the project
2. Follow the instructions in [SETUP.md](file://d:\вуз\bd_project\SETUP.md) to deploy the database
3. Examine [database_design.md](file://d:\вуз\bd_project\database_design.md) to understand the schema design
4. Review [schema.sql](file://d:\вуз\bd_project\schema.sql) to see the actual database implementation
5. Run [fraud_detection.py](file://d:\вуз\bd_project\fraud_detection.py) to see the fraud detection algorithms in action
6. Set up and run the security dashboard from the [security_dashboard/](file://d:\вуз\bd_project\security_dashboard) directory