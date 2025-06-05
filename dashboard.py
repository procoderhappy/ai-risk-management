"""
Streamlit Dashboard for AI Risk Management System
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time

# Page configuration
st.set_page_config(
    page_title="AI Risk Management Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .risk-high {
        border-left-color: #ff4b4b !important;
    }
    .risk-medium {
        border-left-color: #ffa500 !important;
    }
    .risk-low {
        border-left-color: #00cc00 !important;
    }
    .sidebar-content {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_token' not in st.session_state:
    st.session_state.user_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

def make_api_request(endpoint, method="GET", data=None, headers=None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if headers is None:
            headers = {}
        
        if st.session_state.user_token:
            headers["Authorization"] = f"Bearer {st.session_state.user_token}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API server. Please ensure the server is running.")
        return None
    except Exception as e:
        st.error(f"Error making API request: {str(e)}")
        return None

def login_page():
    """Login page"""
    st.markdown('<h1 class="main-header">🏦 AI Risk Management System</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Login")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                if username and password:
                    # Simulate login (in real implementation, call API)
                    if username == "admin" and password == "admin123":
                        st.session_state.authenticated = True
                        st.session_state.user_token = "demo_token_12345"
                        st.session_state.user_info = {
                            "username": username,
                            "role": "admin",
                            "region": "US"
                        }
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Use admin/admin123 for demo.")
                else:
                    st.error("Please enter both username and password.")
        
        st.markdown("---")
        st.info("**Demo Credentials:**\nUsername: admin\nPassword: admin123")

def sidebar():
    """Sidebar navigation"""
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        # User info
        if st.session_state.user_info:
            st.markdown(f"**Welcome, {st.session_state.user_info['username']}**")
            st.markdown(f"Role: {st.session_state.user_info['role']}")
            st.markdown(f"Region: {st.session_state.user_info['region']}")
            st.markdown("---")
        
        # Navigation
        page = st.selectbox(
            "Navigate to:",
            [
                "Dashboard Overview",
                "Risk Assessments",
                "Compliance Monitoring",
                "Document Management",
                "Alert Center",
                "Analytics & Reports",
                "System Settings"
            ]
        )
        
        # Quick actions
        st.markdown("### Quick Actions")
        if st.button("🔍 New Risk Assessment"):
            st.session_state.show_risk_form = True
        
        if st.button("📄 Upload Document"):
            st.session_state.show_upload_form = True
        
        if st.button("⚠️ Create Alert"):
            st.session_state.show_alert_form = True
        
        # Logout
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user_token = None
            st.session_state.user_info = None
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return page

def dashboard_overview():
    """Main dashboard overview"""
    st.markdown('<h1 class="main-header">📊 Dashboard Overview</h1>', unsafe_allow_html=True)
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Risk Assessments", "1,247", "+23")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card risk-low">', unsafe_allow_html=True)
        st.metric("Compliance Score", "94.2%", "+1.2%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card risk-medium">', unsafe_allow_html=True)
        st.metric("Active Alerts", "12", "-3")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Documents Processed", "3,456", "+156")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Risk Trends (Last 30 Days)")
        
        # Generate sample data
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        risk_scores = [0.45 + 0.1 * (i % 7) / 7 + 0.05 * (i % 3) / 3 for i in range(len(dates))]
        
        df_risk = pd.DataFrame({
            'Date': dates,
            'Risk Score': risk_scores
        })
        
        fig_risk = px.line(df_risk, x='Date', y='Risk Score', 
                          title="Average Daily Risk Score",
                          color_discrete_sequence=['#1f77b4'])
        fig_risk.update_layout(height=300)
        st.plotly_chart(fig_risk, use_container_width=True)
    
    with col2:
        st.subheader("Risk Distribution")
        
        risk_data = {
            'Risk Level': ['Low', 'Moderate', 'High', 'Critical'],
            'Count': [450, 320, 180, 45]
        }
        df_risk_dist = pd.DataFrame(risk_data)
        
        fig_pie = px.pie(df_risk_dist, values='Count', names='Risk Level',
                        color_discrete_sequence=['#00cc00', '#ffa500', '#ff6b6b', '#ff4b4b'])
        fig_pie.update_layout(height=300)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Activity")
    
    recent_activities = [
        {"Time": "2 minutes ago", "Activity": "High-risk assessment completed", "Type": "Risk", "Status": "⚠️"},
        {"Time": "15 minutes ago", "Activity": "Compliance check passed", "Type": "Compliance", "Status": "✅"},
        {"Time": "1 hour ago", "Activity": "Document processed successfully", "Type": "Document", "Status": "✅"},
        {"Time": "2 hours ago", "Activity": "Alert resolved", "Type": "Alert", "Status": "✅"},
        {"Time": "3 hours ago", "Activity": "New user registered", "Type": "System", "Status": "ℹ️"}
    ]
    
    df_activity = pd.DataFrame(recent_activities)
    st.dataframe(df_activity, use_container_width=True, hide_index=True)

def risk_assessments_page():
    """Risk assessments page"""
    st.markdown('<h1 class="main-header">🎯 Risk Assessments</h1>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        assessment_type = st.selectbox("Assessment Type", 
                                     ["All", "Credit", "Market", "Operational", "Compliance"])
    
    with col2:
        risk_level = st.selectbox("Risk Level", 
                                ["All", "Low", "Moderate", "High", "Critical"])
    
    with col3:
        region = st.selectbox("Region", 
                            ["All", "US", "EU", "UK", "APAC"])
    
    with col4:
        date_range = st.selectbox("Date Range", 
                                ["Last 7 days", "Last 30 days", "Last 90 days", "Custom"])
    
    # Risk assessment table
    st.subheader("Risk Assessments")
    
    # Sample data
    assessments_data = [
        {"ID": "RA-001", "Type": "Credit", "Risk Level": "High", "Score": 0.78, "Date": "2024-06-05", "Status": "Completed"},
        {"ID": "RA-002", "Type": "Market", "Risk Level": "Moderate", "Score": 0.45, "Date": "2024-06-04", "Status": "Completed"},
        {"ID": "RA-003", "Type": "Operational", "Risk Level": "Low", "Score": 0.23, "Date": "2024-06-04", "Status": "Completed"},
        {"ID": "RA-004", "Type": "Compliance", "Risk Level": "Critical", "Score": 0.89, "Date": "2024-06-03", "Status": "Under Review"},
        {"ID": "RA-005", "Type": "Credit", "Risk Level": "Moderate", "Score": 0.56, "Date": "2024-06-03", "Status": "Completed"}
    ]
    
    df_assessments = pd.DataFrame(assessments_data)
    
    # Color code risk levels
    def color_risk_level(val):
        if val == "Critical":
            return "background-color: #ffebee"
        elif val == "High":
            return "background-color: #fff3e0"
        elif val == "Moderate":
            return "background-color: #f3e5f5"
        else:
            return "background-color: #e8f5e8"
    
    styled_df = df_assessments.style.applymap(color_risk_level, subset=['Risk Level'])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # New assessment form
    if st.session_state.get('show_risk_form', False):
        st.subheader("Create New Risk Assessment")
        
        with st.form("risk_assessment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_type = st.selectbox("Assessment Type", 
                                      ["Credit", "Market", "Operational", "Compliance"])
                new_region = st.selectbox("Region", ["US", "EU", "UK", "APAC"])
            
            with col2:
                document_id = st.text_input("Document ID (optional)")
                description = st.text_area("Description")
            
            submit = st.form_submit_button("Create Assessment")
            cancel = st.form_submit_button("Cancel")
            
            if submit:
                st.success("Risk assessment created successfully!")
                st.session_state.show_risk_form = False
                st.rerun()
            
            if cancel:
                st.session_state.show_risk_form = False
                st.rerun()

def compliance_monitoring_page():
    """Compliance monitoring page"""
    st.markdown('<h1 class="main-header">📋 Compliance Monitoring</h1>', unsafe_allow_html=True)
    
    # Compliance overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card risk-low">', unsafe_allow_html=True)
        st.metric("Overall Compliance", "94.2%", "+1.2%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Compliant Checks", "156", "+12")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card risk-medium">', unsafe_allow_html=True)
        st.metric("Non-Compliant", "8", "-2")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Compliance by regulation
    st.subheader("Compliance by Regulation")
    
    compliance_data = {
        'Regulation': ['GDPR', 'SOX', 'Basel III', 'MiFID II', 'HIPAA'],
        'Score': [96.5, 94.2, 92.8, 95.1, 93.7],
        'Status': ['Compliant', 'Compliant', 'Compliant', 'Compliant', 'Review Required']
    }
    
    df_compliance = pd.DataFrame(compliance_data)
    
    fig_compliance = px.bar(df_compliance, x='Regulation', y='Score',
                           title="Compliance Scores by Regulation",
                           color='Score',
                           color_continuous_scale='RdYlGn')
    fig_compliance.update_layout(height=400)
    st.plotly_chart(fig_compliance, use_container_width=True)
    
    # Recent compliance checks
    st.subheader("Recent Compliance Checks")
    
    checks_data = [
        {"Check ID": "CC-001", "Regulation": "GDPR", "Status": "Compliant", "Score": 96.5, "Date": "2024-06-05"},
        {"Check ID": "CC-002", "Regulation": "SOX", "Status": "Compliant", "Score": 94.2, "Date": "2024-06-04"},
        {"Check ID": "CC-003", "Regulation": "Basel III", "Status": "Review Required", "Score": 78.5, "Date": "2024-06-04"},
        {"Check ID": "CC-004", "Regulation": "MiFID II", "Status": "Compliant", "Score": 95.1, "Date": "2024-06-03"}
    ]
    
    df_checks = pd.DataFrame(checks_data)
    st.dataframe(df_checks, use_container_width=True, hide_index=True)

def document_management_page():
    """Document management page"""
    st.markdown('<h1 class="main-header">📄 Document Management</h1>', unsafe_allow_html=True)
    
    # Upload section
    if st.session_state.get('show_upload_form', False):
        st.subheader("Upload Document")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'docx', 'txt', 'csv', 'xlsx'],
            help="Supported formats: PDF, DOCX, TXT, CSV, XLSX"
        )
        
        if uploaded_file is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Upload & Process"):
                    st.success(f"File '{uploaded_file.name}' uploaded successfully!")
                    st.info("Document processing started...")
                    st.session_state.show_upload_form = False
                    st.rerun()
            
            with col2:
                if st.button("Cancel Upload"):
                    st.session_state.show_upload_form = False
                    st.rerun()
    
    # Document statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Documents", "3,456", "+156")
    
    with col2:
        st.metric("Processed", "3,234", "+142")
    
    with col3:
        st.metric("Processing", "18", "+8")
    
    with col4:
        st.metric("Failed", "4", "+6")
    
    # Document list
    st.subheader("Recent Documents")
    
    documents_data = [
        {"Filename": "financial_report_q1.pdf", "Type": "PDF", "Size": "2.3 MB", "Status": "Processed", "Uploaded": "2024-06-05"},
        {"Filename": "compliance_audit.docx", "Type": "DOCX", "Size": "1.8 MB", "Status": "Processing", "Uploaded": "2024-06-05"},
        {"Filename": "risk_data.xlsx", "Type": "XLSX", "Size": "5.2 MB", "Status": "Processed", "Uploaded": "2024-06-04"},
        {"Filename": "policy_document.pdf", "Type": "PDF", "Size": "1.1 MB", "Status": "Processed", "Uploaded": "2024-06-04"},
        {"Filename": "transaction_log.csv", "Type": "CSV", "Size": "12.5 MB", "Status": "Failed", "Uploaded": "2024-06-03"}
    ]
    
    df_documents = pd.DataFrame(documents_data)
    st.dataframe(df_documents, use_container_width=True, hide_index=True)

def alert_center_page():
    """Alert center page"""
    st.markdown('<h1 class="main-header">⚠️ Alert Center</h1>', unsafe_allow_html=True)
    
    # Alert statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card risk-high">', unsafe_allow_html=True)
        st.metric("Critical Alerts", "3", "+1")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card risk-medium">', unsafe_allow_html=True)
        st.metric("High Priority", "9", "-2")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.metric("Medium Priority", "15", "+5")
    
    with col4:
        st.metric("Low Priority", "23", "+8")
    
    # Alert filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        alert_type = st.selectbox("Alert Type", 
                                ["All", "Risk Threshold", "Compliance Violation", "System Error"])
    
    with col2:
        alert_severity = st.selectbox("Severity", 
                                    ["All", "Critical", "High", "Medium", "Low"])
    
    with col3:
        alert_status = st.selectbox("Status", 
                                  ["All", "Active", "Acknowledged", "Resolved"])
    
    # Active alerts
    st.subheader("Active Alerts")
    
    alerts_data = [
        {"ID": "ALT-001", "Type": "Risk Threshold", "Severity": "Critical", "Title": "Credit risk threshold exceeded", "Created": "2024-06-05 14:30", "Status": "Active"},
        {"ID": "ALT-002", "Type": "Compliance Violation", "Severity": "High", "Title": "GDPR compliance issue detected", "Created": "2024-06-05 12:15", "Status": "Acknowledged"},
        {"ID": "ALT-003", "Type": "System Error", "Severity": "Medium", "Title": "Document processing failure", "Created": "2024-06-05 10:45", "Status": "Active"},
        {"ID": "ALT-004", "Type": "Risk Threshold", "Severity": "High", "Title": "Market volatility alert", "Created": "2024-06-04 16:20", "Status": "Resolved"},
        {"ID": "ALT-005", "Type": "Compliance Violation", "Severity": "Low", "Title": "Minor policy deviation", "Created": "2024-06-04 14:10", "Status": "Active"}
    ]
    
    df_alerts = pd.DataFrame(alerts_data)
    
    # Color code severity
    def color_severity(val):
        if val == "Critical":
            return "background-color: #ffebee"
        elif val == "High":
            return "background-color: #fff3e0"
        elif val == "Medium":
            return "background-color: #f3e5f5"
        else:
            return "background-color: #e8f5e8"
    
    styled_alerts = df_alerts.style.applymap(color_severity, subset=['Severity'])
    st.dataframe(styled_alerts, use_container_width=True, hide_index=True)

def analytics_reports_page():
    """Analytics and reports page"""
    st.markdown('<h1 class="main-header">📈 Analytics & Reports</h1>', unsafe_allow_html=True)
    
    # Analytics tabs
    tab1, tab2, tab3 = st.tabs(["Risk Analytics", "Compliance Trends", "Performance Metrics"])
    
    with tab1:
        st.subheader("Risk Analytics")
        
        # Risk heatmap
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Risk Heatmap by Type and Level**")
            
            # Sample heatmap data
            import numpy as np
            risk_types = ['Credit', 'Market', 'Operational', 'Compliance']
            risk_levels = ['Low', 'Moderate', 'High', 'Critical']
            
            heatmap_data = np.random.randint(1, 20, size=(len(risk_types), len(risk_levels)))
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=heatmap_data,
                x=risk_levels,
                y=risk_types,
                colorscale='RdYlBu_r'
            ))
            fig_heatmap.update_layout(height=300)
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        with col2:
            st.write("**Risk Score Distribution**")
            
            # Risk score histogram
            risk_scores = np.random.beta(2, 5, 1000)  # Sample risk scores
            
            fig_hist = px.histogram(x=risk_scores, nbins=30, 
                                  title="Risk Score Distribution",
                                  labels={'x': 'Risk Score', 'y': 'Frequency'})
            fig_hist.update_layout(height=300)
            st.plotly_chart(fig_hist, use_container_width=True)
    
    with tab2:
        st.subheader("Compliance Trends")
        
        # Compliance trends over time
        dates = pd.date_range(start=datetime.now() - timedelta(days=90), end=datetime.now(), freq='D')
        compliance_scores = [90 + 5 * np.sin(i/10) + np.random.normal(0, 1) for i in range(len(dates))]
        
        df_compliance_trend = pd.DataFrame({
            'Date': dates,
            'Compliance Score': compliance_scores
        })
        
        fig_compliance_trend = px.line(df_compliance_trend, x='Date', y='Compliance Score',
                                     title="Compliance Score Trends (Last 90 Days)")
        fig_compliance_trend.update_layout(height=400)
        st.plotly_chart(fig_compliance_trend, use_container_width=True)
    
    with tab3:
        st.subheader("Performance Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("API Response Time", "245ms", "-15ms")
            st.metric("Document Processing Rate", "98.7%", "+0.3%")
            st.metric("System Uptime", "99.9%", "0%")
        
        with col2:
            st.metric("Active Users", "127", "+12")
            st.metric("Daily Transactions", "15,432", "+1,234")
            st.metric("Error Rate", "0.12%", "-0.05%")

def system_settings_page():
    """System settings page"""
    st.markdown('<h1 class="main-header">⚙️ System Settings</h1>', unsafe_allow_html=True)
    
    # Settings tabs
    tab1, tab2, tab3 = st.tabs(["User Management", "System Configuration", "Audit Logs"])
    
    with tab1:
        st.subheader("User Management")
        
        # User list
        users_data = [
            {"Username": "admin", "Role": "Admin", "Region": "US", "Status": "Active", "Last Login": "2024-06-05 15:30"},
            {"Username": "manager1", "Role": "Manager", "Region": "EU", "Status": "Active", "Last Login": "2024-06-05 14:20"},
            {"Username": "analyst1", "Role": "Analyst", "Region": "US", "Status": "Active", "Last Login": "2024-06-05 13:45"},
            {"Username": "viewer1", "Role": "Viewer", "Region": "APAC", "Status": "Inactive", "Last Login": "2024-06-03 09:15"}
        ]
        
        df_users = pd.DataFrame(users_data)
        st.dataframe(df_users, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("System Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Risk Thresholds**")
            low_threshold = st.slider("Low Risk Threshold", 0.0, 1.0, 0.3)
            moderate_threshold = st.slider("Moderate Risk Threshold", 0.0, 1.0, 0.6)
            high_threshold = st.slider("High Risk Threshold", 0.0, 1.0, 0.8)
        
        with col2:
            st.write("**Compliance Settings**")
            compliance_threshold = st.slider("Compliance Threshold", 0, 100, 85)
            audit_frequency = st.selectbox("Audit Frequency", ["Weekly", "Monthly", "Quarterly"])
            auto_alerts = st.checkbox("Enable Automatic Alerts", True)
    
    with tab3:
        st.subheader("Audit Logs")
        
        # Audit log filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            log_user = st.selectbox("User", ["All", "admin", "manager1", "analyst1"])
        
        with col2:
            log_action = st.selectbox("Action", ["All", "Login", "Create", "Update", "Delete"])
        
        with col3:
            log_date = st.date_input("Date", datetime.now().date())
        
        # Sample audit logs
        audit_logs = [
            {"Timestamp": "2024-06-05 15:30:25", "User": "admin", "Action": "Login", "Resource": "System", "IP": "192.168.1.100"},
            {"Timestamp": "2024-06-05 15:25:10", "User": "admin", "Action": "Create", "Resource": "Risk Assessment", "IP": "192.168.1.100"},
            {"Timestamp": "2024-06-05 14:20:15", "User": "manager1", "Action": "Update", "Resource": "Compliance Check", "IP": "192.168.1.101"},
            {"Timestamp": "2024-06-05 13:45:30", "User": "analyst1", "Action": "View", "Resource": "Document", "IP": "192.168.1.102"}
        ]
        
        df_audit = pd.DataFrame(audit_logs)
        st.dataframe(df_audit, use_container_width=True, hide_index=True)

def main():
    """Main application"""
    if not st.session_state.authenticated:
        login_page()
    else:
        # Sidebar navigation
        page = sidebar()
        
        # Main content
        if page == "Dashboard Overview":
            dashboard_overview()
        elif page == "Risk Assessments":
            risk_assessments_page()
        elif page == "Compliance Monitoring":
            compliance_monitoring_page()
        elif page == "Document Management":
            document_management_page()
        elif page == "Alert Center":
            alert_center_page()
        elif page == "Analytics & Reports":
            analytics_reports_page()
        elif page == "System Settings":
            system_settings_page()

if __name__ == "__main__":
    main()