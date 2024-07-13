import streamlit as st
import pandas as pd
from PIL import Image
import base64
import io

# Funções para manipular dados CSV
def load_companies():
    try:
        return pd.read_csv('empresas.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Nome', 'Logo'])

def save_companies(df):
    df.to_csv('empresas.csv', index=False)

def load_products():
    try:
        return pd.read_csv('produtos.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Empresa', 'Código', 'Descrição título', 'Qtd. Vol.', 'Marca', 'Modelo', 'Fabr.'])

def save_products(df):
    df.to_csv('produtos.csv', index=False)

# Carregar dados
companies_df = load_companies()
products_df = load_products()

# Função para converter imagem para base64
def image_to_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Função para salvar produto
def save_product(company, product_data):
    global products_df
    product_data['Empresa'] = company
    products_df = pd.concat([products_df, pd.DataFrame([product_data])], ignore_index=True)
    save_products(products_df)
    st.success(f"Produto salvo para {company}!")

# Função para salvar empresa
def save_company(name, logo):
    global companies_df
    logo_base64 = image_to_base64(logo) if logo else None
    new_company = pd.DataFrame({'Nome': [name], 'Logo': [logo_base64]})
    companies_df = pd.concat([companies_df, new_company], ignore_index=True)
    save_companies(companies_df)
    st.success(f"Empresa {name} cadastrada com sucesso!")

# Função para editar empresa
def edit_company(old_name, new_name, logo):
    global companies_df
    if new_name != old_name and new_name in companies_df['Nome'].values:
        st.warning(f"A empresa {new_name} já existe.")
        return
    logo_base64 = image_to_base64(logo) if logo else companies_df.loc[companies_df['Nome'] == old_name, 'Logo'].values[0]
    companies_df.loc[companies_df['Nome'] == old_name, 'Nome'] = new_name
    companies_df.loc[companies_df['Nome'] == new_name, 'Logo'] = logo_base64
    products_df.loc[products_df['Empresa'] == old_name, 'Empresa'] = new_name
    save_companies(companies_df)
    save_products(products_df)
    st.success(f"Empresa {old_name} editada para {new_name}!")

# Layout do aplicativo
st.sidebar.title("Menu")
menu = st.sidebar.radio("Escolha uma opção", ["Selecionar Empresa", "Cadastrar Empresa", "Editar Empresa"])

if menu == "Selecionar Empresa":
    st.sidebar.title("Selecione a Empresa")
    company = st.sidebar.selectbox("Empresa", companies_df['Nome'])

    if not companies_df.empty:
        logo_base64 = companies_df.loc[companies_df['Nome'] == company, 'Logo'].values[0]
        if logo_base64:
            st.image(base64.b64decode(logo_base64), width=100)

    st.title(f"Produtos de {company}")

    action = st.sidebar.radio("Escolha uma ação", ["Novo produto", "Consultar Produto"])

    if action == "Novo produto":
        st.header("Cadastro de Produto")
        
        code = st.text_input("Código")
        description = st.text_input("Descrição título")
        qty = st.text_input("Qtd. Vol.")
        brand = st.text_input("Marca")
        model = st.text_input("Modelo")
        manufacturer = st.text_input("Fabr.")
        
        if st.button("Salvar produto"):
            product_data = {
                'Código': code,
                'Descrição título': description,
                'Qtd. Vol.': qty,
                'Marca': brand,
                'Modelo': model,
                'Fabr.': manufacturer
            }
            save_product(company, product_data)
        
    elif action == "Consultar Produto":
        st.header("Produtos Cadastrados")
        
        company_products = products_df[products_df['Empresa'] == company]
        if not company_products.empty:
            st.table(company_products)
        else:
            st.write("Nenhum produto cadastrado.")

    # Excluir produto (opcional)
    if st.button("Excluir produto"):
        company_products = products_df[products_df['Empresa'] == company]
        if not company_products.empty:
            products_df.drop(company_products.index[-1], inplace=True)
            save_products(products_df)
            st.success(f"Último produto excluído de {company}!")
        else:
            st.warning("Nenhum produto para excluir.")

elif menu == "Cadastrar Empresa":
    st.header("Cadastro de Empresa")
    
    company_name = st.text_input("Nome da Empresa")
    logo = st.file_uploader("Upload da Logo", type=["png", "jpg", "jpeg"])
    
    if st.button("Salvar empresa"):
        if company_name and logo:
            logo_image = Image.open(logo)
            save_company(company_name, logo_image)
        else:
            st.warning("Por favor, preencha o nome da empresa e faça o upload da logo.")

elif menu == "Editar Empresa":
    st.header("Editar Empresa")
    
    if not companies_df.empty:
        old_company_name = st.selectbox("Selecione a Empresa para Editar", companies_df['Nome'])
        new_company_name = st.text_input("Novo Nome da Empresa", value=old_company_name)
        new_logo = st.file_uploader("Upload da Nova Logo", type=["png", "jpg", "jpeg"])

        if st.button("Salvar alterações"):
            logo_image = Image.open(new_logo) if new_logo else None
            edit_company(old_company_name, new_company_name, logo_image)
    else:
        st.write("Nenhuma empresa cadastrada.")
