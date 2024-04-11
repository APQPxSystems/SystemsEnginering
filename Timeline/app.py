# Import Libraries
import streamlit as st
import pandas as pd
import sqlite3
import altair as alt
from io import StringIO

# App Configurations
st.set_page_config(page_title='SE Activities', layout='wide')
hide_st_style = """
                <style>
                #MainMenu {visibility:hidden;}
                footer {visibility:hidden;}
                header {visibility:hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Remove top white space
st.markdown("""
        <style>
            .block-container {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)

# Function to create a database
def create_table():
    conn = sqlite3.connect('se_timeline.db')
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS timeline
        (
            id INTEGER PRIMARY KEY,
            requested_app TEXT,
            requestor TEXT,
            section TEXT,
            urgency TEXT,
            date_requested DATE,
            target_start_date DATE,
            target_end_date DATE,
            actual_start_date DATE,
            actual_end_date DATE,
            developer TEXT,
            remarks TEXT
        )
        '''
    )
    conn.commit()
    conn.close()

# Function to insert data into the database
def insert_data(requested_app, requestor, section, urgency, date_requested, target_start_date, target_end_date, actual_start_date, actual_end_date, developer, remarks):
    conn = sqlite3.connect('se_timeline.db')
    c = conn.cursor()
    c.execute(
        '''INSERT INTO timeline (requested_app, requestor, section, urgency, date_requested, target_start_date, target_end_date, actual_start_date, actual_end_date, developer, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (requested_app, requestor, section, urgency, date_requested, target_start_date, target_end_date, actual_start_date, actual_end_date, developer, remarks)
    )
    conn.commit()
    conn.close()
    
# Function to delete data from the database
def delete_data(task_id):
    conn = sqlite3.connect('se_timeline.db')
    c = conn.cursor()
    c.execute('''DELETE FROM timeline WHERE id = ?''', (task_id,))
    conn.commit()
    conn.close()
    
# Function to update data in the database
def update_data(task_id, requested_app, requestor, section, urgency, date_requested, target_start_date, target_end_date, actual_start_date, actual_end_date, developer, remarks):
    conn = sqlite3.connect('se_timeline.db')
    c = conn.cursor()
    c.execute('''UPDATE timeline SET requested_app=?, requestor=?, section=?, urgency=?, 
                date_requested=?, target_start_date=?, target_end_date=?, actual_start_date=?,
                actual_end_date=?, developer=?, remarks=?
                WHERE id=?
            ''', (requested_app, requestor, section, urgency, date_requested, target_start_date, 
                    target_end_date, actual_start_date, actual_end_date, developer, remarks, task_id))
    conn.commit()
    conn.close()

# Function to display data from the database as a pandas dataframe
def display_data_as_df():
    conn = sqlite3.connect('se_timeline.db')
    df = pd.read_sql_query('SELECT * FROM timeline', conn)
    conn.close()
    return df
    
# Function to handle file upload and concatenate with the database
def upload_timeline_file(file):
    if file is not None:
        content = file.read().decode('utf-8')  # Decode bytes to string
        # Assuming the file is a CSV file
        uploaded_df = pd.read_csv(StringIO(content))
        
        # Generate unique IDs for the uploaded DataFrame
        last_id = display_data_as_df()['id'].max()
        if pd.isnull(last_id):
            last_id = 0
        else:
            last_id = int(last_id)  # Cast to integer
        uploaded_df['id'] = range(last_id + 1, last_id + 1 + len(uploaded_df))
        
        # Concatenate the uploaded data with the existing database
        concatenated_df = pd.concat([display_data_as_df(), uploaded_df], ignore_index=True)
        # Update the database with concatenated data
        conn = sqlite3.connect('pe_pdca.db')
        concatenated_df.to_sql('pdca', conn, if_exists='replace', index=False)
        conn.close()
        st.success('PDCA data uploaded and concatenated successfully.')

# Function to delete all contents of the database
def delete_all_data():
    conn = sqlite3.connect('se_timeline.db')
    c = conn.cursor()
    c.execute('''DELETE FROM timeline''')
    conn.commit()
    conn.close()
    st.success('All data deleted successfully!')

# Function to edit data in the database
def edit_timeline():
    df = display_data_as_df()
    st.subheader('Edit Timeline Entries')
    if not df.empty:
        task_id_to_edit = st.selectbox('Select task to edit', df['id'].tolist())
        selected_task = df[df['id'] == task_id_to_edit].iloc[0]
        
        edited_requested_app = st.text_input('Edit Requested App', value=selected_task['requested_app'])
        edited_requestor = st.text_input('Edit Requestor', value=selected_task['requestor'])
        edited_section = st.text_input('Edit Section', value=selected_task['section'])
        edited_urgency = st.text_input('Edit Urgency', value=selected_task['urgency'])
        edited_date_requested = st.date_input('Edit Date Requested', value=pd.to_datetime(selected_task['date_requested']))
        edited_target_start_date = st.date_input('Edit Target Start Date', value=pd.to_datetime(selected_task['target_start_date']))
        edited_target_end_date = st.date_input('Edit Target End Date', value=pd.to_datetime(selected_task['target_end_date']))
        edited_actual_start_date = st.date_input('Edit Actual Start Date', value=pd.to_datetime(selected_task['actual_start_date']))
        edited_actual_end_date = st.date_input('Edit Actual End Date', value=pd.to_datetime(selected_task['actual_end_date']))
        edited_developer = st.text_input('Edit Developer', value=selected_task['developer'])
        edited_remarks = st.text_input('Edit Remarks', value=selected_task['remarks'])
        
        if st.button('Update Data'):
            update_data(task_id_to_edit, edited_requested_app, edited_requestor, edited_section, edited_urgency,
                        edited_date_requested, edited_target_start_date, edited_target_end_date, edited_actual_start_date,
                        edited_actual_end_date, edited_developer, edited_remarks)
            st.success('Data updated successfully.')
    else:
        st.info('No timeline entries to edit.')

# Main function to run the streamlit app
def main():
    # App title and info
    st.markdown("<p class='app_sub_title'>MANUFACTURING ENGINEERING DEPARTMENT | SYSTEMS ENGINEERING</p>", unsafe_allow_html=True)
    st.markdown("<p class='tagline'>Mitigating Encumbrances; Moving towards Excellence</p>", unsafe_allow_html=True)
    st.write('________________________________________________')
    st.markdown("<p class='app_title'>SYSTEMS ENGINEERING TIMELINE OF ACTIVITIES</p>", unsafe_allow_html=True)
    
    # Create table if it doesn't exist
    create_table()
    
    # Select user role
    st.markdown("<p class='app_sub_title'>SELECT USER TYPE TO CONTINUE</p>", unsafe_allow_html=True)
    role_col, pass_col = st.columns([1,1])
    with role_col:
        user_role = st.selectbox('Select user type', ['Viewer', 'Editor'])
    with pass_col:
        user_pass = st.text_input('Input user password', type='password')
    
    # User role -- editor
    if user_role == 'Editor' and user_pass == 'SEadmin':
        df = display_data_as_df()

        # Choose desired activity
        desired_activity = st.selectbox('What do you want to do?', ['View data', 'Add task', 'Edit task', 'Delete task'])
        st.write('________________________________________________')
        
        if desired_activity == 'View data':
            st.subheader('View Timeline Data')
            st.write(df)
            st.write('________________________________________________')
        
        if desired_activity == 'Add task':
            st.subheader('Add New Task')
            requested_app = st.text_input('Requested App')
            requestor_col, section_col = st.columns([1,1])
            with requestor_col:
                requestor = st.text_input('Requestor')
            with section_col:
                section = st.text_input('Section')
            urgency_col, date_requested_col = st.columns([1,1])
            with urgency_col:
                urgency = st.selectbox('Urgency', ['Low', 'Medium', 'High'])
            with date_requested_col:
                date_requested = st.date_input('Date Requested')
            target_start_date_col, target_end_date_col = st.columns([1,1])
            with target_start_date_col:
                target_start_date = st.date_input('Target Start Date')
            with target_end_date_col:
                target_end_date = st.date_input('Target End Date')
            actual_start_date_col, actual_end_date_col = st.columns([1,1])
            with actual_start_date_col:
                actual_start_date = st.date_input('Actual Start Date')
            with actual_end_date_col:
                actual_end_date = st.date_input('Actual End Date')
            developer_col, remarks_col = st.columns([1,1])
            with developer_col:
                developer = st.text_input('Developer')
            with remarks_col:
                remarks = st.text_input('Remarks')
            
            if st.button('Add Task'):
                insert_data(requested_app, requestor, section, urgency, date_requested, target_start_date, target_end_date, actual_start_date, actual_end_date, developer, remarks)
                st.success('Task added successfully.')
        
        if desired_activity == 'Edit task':
            st.subheader('Edit Task')
            task_id_to_edit = st.selectbox('Select task to edit', df['id'].tolist())
            selected_task = df[df['id'] == task_id_to_edit].iloc[0]
            
            requested_app = st.text_input('Requested App', value=selected_task['requested_app'])
            requestor = st.text_input('Requestor', value=selected_task['requestor'])
            section = st.text_input('Section', value=selected_task['section'])
            urgency = st.selectbox('Urgency', ['Low', 'Medium', 'High'], index=['Low', 'Medium', 'High'].index(selected_task['urgency']))
            date_requested = st.date_input('Date Requested', value=pd.to_datetime(selected_task['date_requested']))
            target_start_date = st.date_input('Target Start Date', value=pd.to_datetime(selected_task['target_start_date']))
            target_end_date = st.date_input('Target End Date', value=pd.to_datetime(selected_task['target_end_date']))
            actual_start_date = st.date_input('Actual Start Date', value=pd.to_datetime(selected_task['actual_start_date']))
            actual_end_date = st.date_input('Actual End Date', value=pd.to_datetime(selected_task['actual_end_date']))
            developer = st.text_input('Developer', value=selected_task['developer'])
            remarks = st.text_area('Remarks', value=selected_task['remarks'])
            
            if st.button('Update Task'):
                update_data(task_id_to_edit, requested_app, requestor, section, urgency, date_requested, target_start_date, target_end_date, actual_start_date, actual_end_date, developer, remarks)
                st.success('Task updated successfully.')
        
        if desired_activity == 'Delete task':
            st.subheader('Delete Task')
            task_id_to_delete = st.selectbox('Select task to delete', df['id'].tolist())
            if st.button('Delete Task'):
                delete_data(task_id_to_delete)
                st.success('Task deleted successfully.')

    # User role -- viewer
    elif user_role == 'Viewer' and user_pass == 'SEviewer':

        request_form = open('pepdca\ME3-SE App Request Form.pdf', 'rb')
        st.download_button(
            'Download Systems Engineering Request Form',
            request_form, file_name='SE Request Form.pdf', mime='pdf'
        )
      
        st.subheader('Systems Engineering Activities')
        df = display_data_as_df()
        st.write(df)
        st.write('________________________________________________')

    else:
        st.warning('Please input the correct password for the chosen user type.')

if __name__ == '__main__':
    main()
    
with open('Timeline/style.css') as f:
    css = f.read()

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
