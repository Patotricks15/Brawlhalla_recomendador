import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
import streamlit as st
import base64

df = pd.read_csv('brawlhallastats.csv')
df_completo = pd.read_excel('clust_brawl.xlsx')
df_completo = df_completo.iloc[:,1:]
df_completo = df_completo.merge(df[['legend','Weapon_1','Weapon_2']], how='left', on='legend')


def render_mpl_table(data, col_width=5.0, row_height=0.625, font_size=18,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) * np.array([col_width, row_height]))
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')
    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in mpl_table._cells.items():
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w',fontsize=22, fontfamily='serif')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax.get_figure(), ax

def RecomendarBrawlhalla(personagem):
    personagem_escolhido = personagem
    df_perso = df_completo[df_completo['legend'] == personagem_escolhido]
    df_cluster_perso = df_completo[df_completo['cluster'] == (df_completo[df_completo['legend'] == personagem_escolhido]['cluster'][df_perso.index[0]])]
    similaridade = 0 - cdist(df_perso.iloc[:,:4], df_cluster_perso.iloc[:,:4], metric='euclidean')
    df_similaridade = pd.DataFrame(similaridade.T, columns=['similaridade']).reset_index().merge(df_cluster_perso.reset_index(drop=True).reset_index(), on='index').drop(columns='index').sort_values('similaridade', ascending = False)
    filtro_1 = df_cluster_perso[df_cluster_perso['legend'] == personagem_escolhido]['Weapon_1'][df_perso.index[0]]
    filtro_2 = df_cluster_perso[df_cluster_perso['legend'] == personagem_escolhido]['Weapon_2'][df_perso.index[0]]

    filtro_maior_1 = (df_cluster_perso['Weapon_1'] == filtro_1) |  (df_cluster_perso['Weapon_2'] == filtro_1)
    filtro_maior_2 = (df_cluster_perso['Weapon_1'] == filtro_2) |  (df_cluster_perso['Weapon_2'] == filtro_2)

    df_arma_igual = df_cluster_perso[filtro_maior_1 | filtro_maior_2]
    recomendacao_1 = df_arma_igual[df_arma_igual['legend'] != personagem_escolhido].merge(df_similaridade)
    recomendacao_1['similaridade'] += recomendacao_1['similaridade'].mean()
    df_recomendados = recomendacao_1.append(df_cluster_perso.append(df_arma_igual).drop_duplicates(keep=False).merge(df_similaridade[['similaridade','legend']], on='legend').sort_values('similaridade', ascending=False).drop(columns='similaridade').iloc[0:,:]).reset_index(drop=True).head(10)[['legend', 'strength', 'dexterity', 'defense', 'speed', 'Weapon_1', 'Weapon_2']].set_index('legend')
    # return print(df_recomendados)
    # fig, ax = render_mpl_table(df_recomendados, header_columns=0, col_width=3, font_size=16)
    # fig.savefig("table.png")
    return st.table(df_recomendados)




@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp {
      background-image: url("data:image/png;base64,%s");
      background-size: cover;
    }
    </style>
    ''' % bin_str

    st.markdown(page_bg_img, unsafe_allow_html=True)
    return





set_png_as_page_bg('wall.jpg')



st.markdown('# Recomendador de personagens - Brawlhalla')
st.write('### Um sistema de recomendação de personagens baseado nos atributos e armas semelhantes')
st.write('')
st.write('')
st.write('')
personagem = st.selectbox('Selecione um personagem:', df_completo['legend'])



RecomendarBrawlhalla(personagem)