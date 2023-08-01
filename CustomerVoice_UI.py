import pandas as pd
import streamlit as st
import subprocess
import random

brands_similar_to_lacoste = [
    "Ralph Lauren",
    "Tommy Hilfiger",
    "Fred Perry",
    "Hugo Boss",
    "Calvin Klein",
    "Burberry",
    "Abercrombie & Fitch",
    "Polo Ralph Lauren",
    "Banana Republic",
    "J.Crew",
    "Scotch & Soda",
    "Paul Smith",
    "AllSaints",
    "Superdry",
    "Massimo Dutti",
    "Kate Spade",
    "Armani Exchange",
    "Sandro",
    "Maje",
    "COS",
    "A.P.C.",
    "Steve Madden",
    "ASOS",
    "Diesel",
    "Swatch",
    "David Yurman",
    "Anthropologie",
    "Urban Outfitters",
    "H&M",
    "Mango",
    "Pull&Bear",
    "Esprit",
    "United Colors of Benetton"  
]



def Treat_file(df):
    df["NPS_fix"] = df["NPS"].apply(lambda x : int(x.split(" ")[0]))
    df["Justif_Amelio"] = df["Justification"] + " - " + df["Amélioration"]
    df["Satisfaction"] =  df["Satisfaction"].apply(lambda x : int(x))
    df["NPS"] =  df["NPS"].apply(lambda x : int(x.split(" ")[0]))
    return df


def Generate_prompt(df,i1,i2,text): 
    random_brand = random.choice(brands_similar_to_lacoste)
    
    list_comm = []
    rand_comm = []
    list_comm = df["Justification"].to_list()
    for comm in list_comm:
        if str(comm) == "nan" :
            list_comm.pop(list_comm.index(comm))
        if "lacoste" in str(comm).lower():
            comm2 = str(comm).lower()
            list_comm.pop(list_comm.index(comm))
            comm2 = comm2.replace("lacoste", random_brand)
            list_comm.append(comm2)
    
    for comm in list_comm:
        if len(str(comm)) > 30:
            rand_comm.append(comm)

    prompt = f"""{text}\n Voici la liste : {list_comm[i1:i2]}"""

    random.shuffle(rand_comm)
    
    obj_prompt = {
        "prompt" : prompt,
        "rand_comm" : rand_comm[:30],
        "rand_brand" : random_brand
    }
    

    return obj_prompt




def copy_to_clipboard(text):
    subprocess.run(['clip'], input=text.strip().encode('utf-16'), check=True)
    is_copied = True
    return is_copied
    
def select_brand(brand_list, index):
    if index < 0 or index >= len(brand_list):
        return None
    return brand_list[index]


st. set_page_config(layout="wide")
st.subheader("1. Uploader le fichier issu de CustomerVoice, en respectant les spec suivantes :")
with st.expander("SPEC FILE", expanded=True):
    st.write("- Format du fichier .xlsx")
    st.write("- Se limiter à des données anonymisées : pas de noms, emails...")
    st.write("- Colonnes obligatoires : 'NPS', 'Satisfaction', 'Justification', 'Amélioration'")
    st.write(" ")
    file = st.file_uploader(label="Importer le fichier de création (.xlsx)", type='.xlsx', key='fileUpload', )
    if file is not None:
        df = pd.read_excel(file)
        df = Treat_file(df)
    
    else:
        df = pd.DataFrame()
  
st.markdown("---")
st.write(" ")


col1, col2 = st.columns([1,1])
with col1:

    st.subheader("2. Rédiger un prompt")
    txt = st.text_area('Prompt / recharger la page pour le prompt par défaut)', '''
    Voci une liste de commentaires, ils ont été reçus après un achat sur le site internet d'une marque de fashion sport.     
    Classe les commentaires en 2 catégories, les positifs et les négatifs. 
    Pour chacune des catégories, fais 3 bullets points avec les thèmes les plus fréquents et donne un commentaire en exemple, aussi compte le nombre de commentaires associés aux thèmes.\n
    ''', height = 250)



with col2:
    st.subheader("3. Utiiser les filtres pour avoir une sélection de commentaires")
    #st.write(isinstance(df["Satisfaction"], pd.DataFrame))
   
    if not df.empty:
        satisfaction_grade_min = int(df["Satisfaction"].min())
        satisfaction_grade_max = int(df["Satisfaction"].max())
        satisfaction_grade = st.slider("Satisfaction grade : ", satisfaction_grade_min ,satisfaction_grade_max, (satisfaction_grade_min ,satisfaction_grade_max) )
        filtered_df = df.loc[(df["Satisfaction"] >= satisfaction_grade[0]) & (df["Satisfaction"] <= satisfaction_grade[1])]


        NPS_grade_min = int(df["NPS"].min())
        NPS_grade_max = int(df["NPS"].max())
        NPS_grade = st.slider("NPS grade : ", NPS_grade_min ,NPS_grade_max, (NPS_grade_min ,NPS_grade_max) )
        filtered_df_2 = filtered_df.loc[(filtered_df["NPS"] >= NPS_grade[0]) & (filtered_df["NPS"] <= NPS_grade[1])]


        nb_comm = st.slider('Selectionner un nombre de commentaires',1, filtered_df_2.shape[0], (1,filtered_df_2.shape[0]))
        st.markdown("---")
        st.write(f"Number of comments selected :  {nb_comm[1] - nb_comm[0]}")
        
        is_copied = False
        
        new_prompt = Generate_prompt(filtered_df_2,nb_comm[0],nb_comm[1],txt)
        prompt = new_prompt["prompt"]
        nb_char_prompt = len(str(prompt))
        st.write(f"Corresponding number of characters :  {nb_char_prompt}")
        
        rand_comm = new_prompt["rand_comm"]
        st.markdown("---")
        st.subheader(new_prompt["rand_brand"])

    else:
        st.stop()
    
   


st.markdown("---")
st.write(" ")


is_copied = copy_to_clipboard(prompt)


st.subheader("4. Copier-Coller dans l'interface ChatGPT le prompt enrichi")
if is_copied == True:
    st.success("Copied ✅ Paste it in ChatGPT UI")
else:
    st.warning("Not Copied - Doi it manually ;)")

st.write(prompt[:1000])

st.markdown("---")
st.write(" ")

colA, colB, colC = st.columns([1,1,1])
with colA:
    rand_commA = rand_comm[:10]
    for com in rand_commA:
        st.write(com)

with colB:
    rand_commB = rand_comm[11:20]
    for com in rand_commB:
        st.write(com)

with colC:
    rand_commC = rand_comm[21:30]
    for com in rand_commC:
        st.write(com)



