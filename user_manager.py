# user_manager.py

import streamlit as st
from models import User
from config import CONFIG

def show_user_management():
    st.header("👥 User Management")
    
    # Add new user section
    with st.expander("➕ Add New User", expanded=True):
        with st.form("add_user_form"):
            email = st.text_input("Email Address*", placeholder="user@example.com")
            
            st.write("**Select Job Roles (Choose up to 5):**")
            selected_roles = []
            cols = st.columns(2)
            for i, role in enumerate(CONFIG["JOB_ROLES"]):
                col = cols[i % 2]
                if col.checkbox(role, key=f"role_{i}"):
                    selected_roles.append(role)
            
            st.write("**Select Job Types:**")
            selected_types = st.multiselect("Job Types", CONFIG["JOB_TYPES"], default=["full-time"])
            
            st.write("**Select Preferred Locations:**")
            selected_locations = st.multiselect("Locations", CONFIG["LOCATIONS"], default=["Remote"])
            
            submitted = st.form_submit_button("💾 Save User Preferences")
            
            if submitted:
                if not email:
                    st.error("Email is required!")
                elif len(selected_roles) == 0:
                    st.error("Please select at least one job role!")
                elif len(selected_roles) > 5:
                    st.error("Please select maximum 5 job roles!")
                elif len(selected_types) == 0:
                    st.error("Please select at least one job type!")
                elif len(selected_locations) == 0:
                    st.error("Please select at least one location!")
                else:
                    result = User.create_user(email, selected_roles, selected_types, selected_locations)
                    if result == "created":
                        st.success(f"✅ User {email} created successfully!")
                    else:
                        st.success(f"✅ User {email} updated successfully!")
                    st.rerun()
    
    # Display existing users
    st.subheader("📋 Existing Users")
    users = User.get_all_users()
    
    if users:
        for user in users:
            with st.expander(f"📧 {user['email']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Job Roles:**")
                    for role in user['job_roles']:
                        st.write(f"• {role}")
                    
                    st.write("**Job Types:**")
                    for job_type in user['job_types']:
                        st.write(f"• {job_type}")
                
                with col2:
                    st.write("**Locations:**")
                    for location in user['locations']:
                        st.write(f"• {location}")
                    
                    st.write(f"**Created:** {user['created_at'].strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**Updated:** {user['updated_at'].strftime('%Y-%m-%d %H:%M')}")
    else:
        st.info("No users found. Add your first user above!")
