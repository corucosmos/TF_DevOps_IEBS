import streamlit as st
import requests
import pandas as pd

# Configuración
API_URL = "http://backend:8000"  # Nombre del servicio en docker-compose
#st.set_page_config(page_title="Panel Administrativo", layout="wide")
st.set_page_config(
        page_title="Admin (User Registration API)",
        page_icon="⚙️", 
        layout="wide",
        initial_sidebar_state="auto",
    )

st.markdown("""
    <style>
    .stImage {
        margin-top: -65px !important;       
    }
    .inline-container {
        margin-top: -55px;
        margin-left: 120px;
        display: flex;
        align-items: center;  # Alinea verticalmente
        gap: 10px;           # Espacio entre imagen y título
    }        
    </style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div class="inline-container">          
        <h1 style="margin: 0; padding: 0;">Admin User Registration API</h1>
    </div>
    """, unsafe_allow_html=True
)

#st.image("⚙️", width=100, output_format="JPEG") 

# Función para autenticación
def login():
    st.sidebar.header("Autenticación")
    username = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Contraseña", type="password")
    
    if st.sidebar.button("Login"):
        try:
            response = requests.post(
                f"{API_URL}/login/",
                data={"username": username, "password": password}
            )
            if response.status_code == 200:
                st.session_state.token = response.json()["access_token"]
                st.session_state.is_admin = response.json().get("is_admin", False)
                st.sidebar.success("Login exitoso")
            else:
                st.sidebar.error("Credenciales inválidas")
        except Exception as e:
            st.sidebar.error(f"Error de conexión: {str(e)}")

# Panel de gestión de usuarios
def user_management():
    st.header("Gestión de Usuarios")
    
    # Crear nuevo usuario
    with st.expander("Crear Usuario"):
        with st.form("create_user"):
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            first_name = st.text_input("Nombre")
            last_name = st.text_input("Apellido")
            is_admin = st.checkbox("Es administrador")
            
            if st.form_submit_button("Crear"):
                try:
                    response = requests.post(
                        f"{API_URL}/admin/users/",
                        json={
                            "email": email,
                            "password": password,
                            "first_name": first_name,
                            "last_name": last_name,
                            "is_admin": is_admin
                        },
                        headers={"Authorization": f"Bearer {st.session_state.token}"}
                    )
                    if response.status_code == 201:
                        st.success("Usuario creado exitosamente")
                    else:
                        st.error(f"Error: {response.json().get('detail', '')}")
                except Exception as e:
                    st.error(f"Error de conexión: {str(e)}")
    
    # Listar usuarios
    st.subheader("Usuarios Registrados")
    try:
        users = requests.get(
            f"{API_URL}/admin/users/",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        ).json()
        
        df = pd.DataFrame(users)
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error al cargar usuarios: {str(e)}")

# Main App
def main():
    if "token" not in st.session_state:
        login()
    else:
        if st.session_state.is_admin:
            user_management()
            
            if st.sidebar.button("Logout"):
                st.session_state.clear()
                st.rerun()
        else:
            st.error("No tienes permisos de administrador")
            if st.sidebar.button("Logout"):
                st.session_state.clear()
                st.rerun()

if __name__ == "__main__":
    main()