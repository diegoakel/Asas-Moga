import pandas as pd
import os
import re
import numpy as np
from numpy import inf
import cv2
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import warnings
import six
import fpdf
import pdfplumber
import re
warnings.filterwarnings("ignore")

def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    ''' Renderiza um Dataframe'''
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax

def plot_asa(geo, position=[1,1,1], figure=0, grade=True, color='black', sections=False):
    '''
    Recebe o "df.iloc[x]"
    '''
    geo = list(geo)#[0:10]   
    
    envs = geo[0:3]
    
    # Isso é para o sem interpolação
    if len(geo) > 21:
        cordas = geo[20:]
    else:
        cordas = geo[3:7]
    
    offsets = []
    
    envs_new = []
    for i in range (0, len(cordas)):
        envs_new.append(i*(max(envs)*2)/(2*(len(cordas)-1)))
        
    envs = envs_new
    
    for i in range (0, len(cordas)):
        if i==0:
            offsets.append(0)
        else:
            offsets.append((cordas[0]-cordas[i])/2)
    
    if figure == 0:
        fig = plt.figure()
    else:
        fig = figure
        
    ax = fig.add_subplot(*position, aspect='equal')
        
    if sections ==False:
        x = [0,envs[0],envs[1],envs[2],envs[2],envs[1],envs[0],0]
        y = [0,offsets[0],offsets[1],offsets[2],offsets[2]+cordas[-1],offsets[1]+cordas[-2],offsets[0]+cordas[-3],cordas[-4]]
        
        # Cobem
        x = envs +  envs[::-1]
        y = offsets + list(np.sum([offsets[::-1], cordas[::-1]], axis=0))
        
        ax.add_patch(patches.Polygon(xy=list(zip(x,y)), fill=False, color="black"))
    
    else:
        # Seção 1
        x = [0,envs[0],envs[0],0]
        y = [0,offsets[0],offsets[0]+cordas[-3],cordas[-4]]
        ax.add_patch(patches.Polygon(xy=list(zip(x,y)), fill=False))
        
        # Seção 2
        x = [envs[0],envs[1],envs[1],envs[0]]
        y = [offsets[0],offsets[1],offsets[1]+cordas[-2],offsets[0]+cordas[-3]]
        ax.add_patch(patches.Polygon(xy=list(zip(x,y)), fill=False))
        
        # Seção 3
        x = [envs[1],envs[2],envs[2],envs[1]]
        y = [offsets[1],offsets[2], offsets[2]+cordas[-1],offsets[1]+cordas[-2]]
        ax.add_patch(patches.Polygon(xy=list(zip(x,y)), fill=False))        
        
    if (color != 0):
        ax.add_patch(patches.Polygon(xy=list(zip(x,y)), fill=True, color=color))

    x = [value*-1 for value in x]
    
    ax.add_patch(patches.Polygon(xy=list(zip(x,y)), fill=False))
                 
    if color!= 0:
        ax.add_patch(patches.Polygon(xy=list(zip(x,y)), fill=True, color=color))

    plt.xlim(min(x)*-1.2, min(x)*1.2)
    plt.ylim(-0.3,max(y)*1.3)
    
    if sections:
        plt.xlim(0, min(x)*1.2*-1)
        
    if grade:
        plt.title(f"")
        
    else:
        plt.axis('off')

def checa_sobrevivencia(df):
    df["Sobreviveu"] = ""
    posicao = 0
    for i in range(0, len(df)-1):
        for x,individuo in enumerate([list(linha[:10]) for linha in df[df["Geracao"] == i].values]):
            if individuo in [list(linha[:10]) for linha in df[df["Geracao"] == i+1].values]:
                df.loc[posicao,"Sobreviveu"] = "Sim"
            else:
                df.loc[posicao,"Sobreviveu"] = "Não"
            posicao +=1
    return df

def animacao(df,file= 'animacao_geracoes'):
    directory = "./plot/"
    linhas = 8
    colunas = 5
    for geracao in range (0, df["Geracao"].nunique()-1):
        f = plt.figure(figsize=(15,8))
        atual  = df[df["Geracao"]==geracao].reset_index(drop=True)
        for i in range(1, len(atual)+1):
            plot_asa(atual.iloc[i-1], [linhas, colunas, i], f, grade=False)
            
        plt.savefig(f"{directory}geracao_{geracao}_0.jpeg", transparent=False)
        
        f = plt.figure(figsize=(15,8))
        for i in range(1, len(atual)+1):
            if atual.loc[i-1, "Sobreviveu"] == "Sim":
                plot_asa(atual.iloc[i-1], [linhas, colunas, i], f, grade=False, color="green")
                
            elif atual.loc[i-1, "Sobreviveu"] == "Não":
                plot_asa(atual.iloc[i-1], [linhas, colunas, i], f, grade=False, color="firebrick")
                
        plt.savefig(f"{directory}geracao_{geracao}_1.jpeg", transparent=False)
    
    # Video
    video_name =directory+file+'.mp4'
    images = [img for img in os.listdir(directory) if img.endswith(".jpeg")]
    frame = cv2.imread(os.path.join(directory, images[0]))
    height, width, layers = frame.shape

    df = pd.DataFrame([image.split("_")[1:3]  for image in images], images).reset_index()
    df.columns = ["file", "geracao", "tipo"]
    df["geracao"] = df["geracao"].astype(int)
    df["tipo"] = df["tipo"].str[0].astype(int)
    df = df.sort_values(by=["geracao", "tipo"])
    images_formatos = list(df[df["tipo"]==0]["file"])
    images_cores = list(df[df["tipo"]==1]["file"])
    images = list(df["file"])

    fps = 5
    video = cv2.VideoWriter(video_name, 0, fps, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(directory, image)))

    cv2.destroyAllWindows()
    video.release()

def ler_logs(arquivo):
    df_final = pd.DataFrame()

    df = pd.read_csv(f"{arquivo}.csv")
    df= df.drop('Unnamed: 0', axis=1)

    for i in ['pop_new', 'objetivos', 'constraints','objetivos_penalizados', 'parameters', 'viavel']:
        df[i] = df[i].apply(lambda x: eval(x))

    variaveis = ["Envergadura_1", "Envergadura_2","Envergadura_3","Corda_1","Corda_2","Corda_3","Corda_4"]
    geometria = pd.DataFrame(df[["pop_new"]].explode("pop_new")["pop_new"].to_list(), columns= variaveis)
    gen_no = df[["gen_no","pop_new"]].explode("pop_new")["gen_no"]
    df_final = pd.concat([df_final,geometria])
    df_final["Geracao"] = gen_no.reset_index(drop=True)

    df_final["Pontuacao"] = df[["objetivos"]].explode("objetivos")["objetivos"].apply(lambda x: x[0]*-1).reset_index(drop="True")

    df_final["constraints"] =  df[["constraints"]].explode("constraints").reset_index(drop=True)["constraints"]

    df_final["objetivos_penalizados"] = df[["objetivos_penalizados"]].explode("objetivos_penalizados")["objetivos_penalizados"].apply(lambda x: x[0]).reset_index(drop="True")

    df_final["viavel"] = df[["viavel"]].explode("viavel").reset_index(drop=True)["viavel"]
    
    parametros = df[["parameters"]].explode("parameters")["parameters"].to_list()
    
    variaveis = ["Area", "CL","CD","Massa_Vazia","a", "b", "c", "d"]
    
    if len(parametros[0]) > 10:
        [variaveis.append(f"Chord_{i}") for i in range(1,12)]
    
    if len(parametros[0]) < 10:
        variaveis.append("extra")
        for i in range(0, len(parametros)):
            if len(parametros[i]) >10:
                parametros[i] = [0]*9
        
    # Ordem dos coef pode estar errada
    if len(parametros[0])==18:
        [param.insert(7,0) for param in parametros]
    
    resultados = pd.DataFrame(parametros, columns= variaveis)
    df_final = pd.concat([df_final, resultados], axis=1)
    
    return df_final


def gerar_relatorio(label, path):
    # file = "Cobem_poly_3_20_300_R3"
    # path = "grau=3/"+ file
    # grau = re.findall(r"grau=\d", path)[0]

    path = path
    df = ler_logs(path)

    df = df[df['viavel']==0]
    ultima = df[df['Geracao']==299]

    ultima = ultima[['Envergadura_1', 'Envergadura_2', 'Envergadura_3', 'Corda_1', 'Corda_2',
        'Corda_3', 'Corda_4', 'Pontuacao', 'Area', 'CL', 'CD', 'Massa_Vazia']]

    ultima = ultima[['Envergadura_1', 'Envergadura_2', 'Envergadura_3', 'Corda_1', 'Corda_2',
        'Corda_3', 'Corda_4', 'Pontuacao']]

    for coluna in ultima.columns:
        ultima[coluna] = ultima[coluna].apply(lambda x: str(x)[:4])
        
    ultima = ultima.rename(columns = {"Envergadura_1": "Env_1", "Envergadura_2": "Env_2","Envergadura_3": "Env_3"})

    ultima = ultima.sort_values("Pontuacao", ascending=False)
    ultima =  ultima.head(20)

    render_mpl_table(ultima, header_columns=0, col_width=2.0)
    plt.savefig('../ultima.png')

    plot_asa(df.loc[11999])
    plt.savefig('../melhor.png')


    # # Visualiações 
    # for i in range(0, len(ultima)):
    #     plot_asa(ultima.iloc[i])

    plt.figure(figsize=(10,8))

    viavel = df[df["viavel"]==0]
    viavel.groupby("Geracao").max()["Pontuacao"].plot()

    plt.title("Cobem Polynomial")
    plt.xlabel("Generation")
    plt.ylabel("Payload (kg)")
    plt.ylim(15,19.5)
    plt.savefig('../payload_generation.png')


    sns.set(font_scale = 1.3)
    plt.figure(figsize=(10,8))
    sns.scatterplot(data= df, x="Area", y="Pontuacao", alpha=1, palette=['black'])

    plt.xlabel("Wing Surface Area ($\mathregular{m^{2}}$)")
    plt.ylabel("Payload (kg)")
    plt.title("Cobem")

    _ = plt.xlim(0,3.5)
    _ = plt.ylim(5,22)
    plt.savefig('../payload_area.png')

    # df = checa_sobrevivencia(df)
    # animacao(df)


    # # Relatório
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_font('arial', 'B', 30)
    pdf.cell(60)
    pdf.cell(75, 10, f"{label}", 0,2,"C")
    pdf.set_font('arial','B' , 11)
    pdf.cell(75, 10, "Ultima Geração", 0,2,"C")
    pdf.cell(90,10, '', 0,2, "C")
    pdf.cell(-55)
    pdf.image('../ultima.png', x=0, y=None, w=200, h=0, type='', link='')
    pdf.image('../payload_generation.png', x=0, y=None, w=200, h=0, type='', link='')
    pdf.image('../payload_area.png', x=0, y=None, w=200, h=0, type='', link='')
    pdf.cell(60)
    pdf.cell(75, 10, "Melhor Asa", 0,2,"C")
    pdf.cell(-60)
    pdf.image('../melhor.png', x=0, y=None, w=200, h=0, type='', link='')
    # grau = path.split("_")[2]
    pdf.output(f'{path}.pdf','F')



