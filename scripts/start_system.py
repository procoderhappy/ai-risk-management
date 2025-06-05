"""
System startup script
"""

import subprocess
import sys
import time
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import streamlit
        import sqlalchemy
        import pandas
        import plotly
        logger.info("All dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        return False

def initialize_database():
    """Initialize the database"""
    try:
        logger.info("Initializing database...")
        from app.utils.database_init import initialize_database
        initialize_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False
    return True

def start_api_server():
    """Start the FastAPI server"""
    try:
        logger.info("Starting API server...")
        # Start API server in background
        api_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", "12000",
            "--reload"
        ])
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if process is still running
        if api_process.poll() is None:
            logger.info("API server started successfully on port 12000")
            return api_process
        else:
            logger.error("API server failed to start")
            return None
            
    except Exception as e:
        logger.error(f"Error starting API server: {e}")
        return None

def start_dashboard():
    """Start the Streamlit dashboard"""
    try:
        logger.info("Starting Streamlit dashboard...")
        # Start dashboard
        dashboard_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.port", "12001",
            "--server.address", "0.0.0.0",
            "--server.allowRunOnSave", "true",
            "--server.enableCORS", "true",
            "--server.enableXsrfProtection", "false"
        ])
        
        # Wait a moment for dashboard to start
        time.sleep(5)
        
        # Check if process is still running
        if dashboard_process.poll() is None:
            logger.info("Dashboard started successfully on port 12001")
            return dashboard_process
        else:
            logger.error("Dashboard failed to start")
            return None
            
    except Exception as e:
        logger.error(f"Error starting dashboard: {e}")
        return None

def main():
    """Main startup function"""
    logger.info("🏦 Starting AI Risk Management System...")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Please install required dependencies: pip install -r requirements.txt")
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        logger.error("Database initialization failed")
        sys.exit(1)
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        logger.error("Failed to start API server")
        sys.exit(1)
    
    # Start dashboard
    dashboard_process = start_dashboard()
    if not dashboard_process:
        logger.error("Failed to start dashboard")
        api_process.terminate()
        sys.exit(1)
    
    logger.info("🚀 System started successfully!")
    logger.info("📊 Dashboard: https://work-2-ikuhkwpyelwffnqd.prod-runtime.all-hands.dev")
    logger.info("🔗 API Docs: https://work-1-ikuhkwpyelwffnqd.prod-runtime.all-hands.dev/docs")
    logger.info("👤 Demo Login: admin / admin123")
    
    try:
        # Keep the script running
        while True:
            time.sleep(10)
            
            # Check if processes are still running
            if api_process.poll() is not None:
                logger.error("API server stopped unexpectedly")
                break
                
            if dashboard_process.poll() is not None:
                logger.error("Dashboard stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        logger.info("Shutting down system...")
        
    finally:
        # Cleanup processes
        if api_process and api_process.poll() is None:
            api_process.terminate()
            logger.info("API server stopped")
            
        if dashboard_process and dashboard_process.poll() is None:
            dashboard_process.terminate()
            logger.info("Dashboard stopped")
        
        logger.info("System shutdown complete")

if __name__ == "__main__":
    main()