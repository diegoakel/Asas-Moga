import pandas as pd
import os
import re
import numpy as np
from numpy import inf
import cv2
from pandas.core.frame import DataFrame
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.ticker as ticker
import warnings
import six
import fpdf
import math
import pdfplumber


def ler_logs(arquivo):
    """
    Lê um dado arquivo de logs raw de otimização e retorna o dataframe equivalente.
    Esse dataframe clean é o utilizado para todas as próximas etapas.

    :param arquivo: Nome do arquivo de logs
    :type arquivo: str
    :return: Dataframe clean do arquivo de logs
    :rtype: DataFrame
    """
    df_final = pd.DataFrame()
    path = f"../Resultados/{arquivo}.csv"
    df = pd.read_csv(path)
    df = df.drop("Unnamed: 0", axis=1)

    for i in [
        "pop_new",
        "objetivos",
        "constraints",
        "objetivos_penalizados",
        "parameters",
        "viavel",
    ]:
        df[i] = df[i].apply(lambda x: eval(x))

    variaveis = [
        "Envergadura_1",
        "Envergadura_2",
        "Envergadura_3",
        "Corda_1",
        "Corda_2",
        "Corda_3",
        "Corda_4",
        "Offset_1",
        "Offset_2",
        "Offset_3",
    ]
    geometria = pd.DataFrame(
        df[["pop_new"]].explode("pop_new")["pop_new"].to_list(), columns=variaveis
    )
    gen_no = df[["gen_no", "pop_new"]].explode("pop_new")["gen_no"]
    df_final = pd.concat([df_final, geometria])
    df_final["Geracao"] = gen_no.reset_index(drop=True)

    if (
        re.findall("tipo=\d", arquivo,)[
            0
        ][-1]
        == "4"
    ):
        df_final["Pontuacao_1"] = (
            df[["objetivos"]]
            .explode("objetivos")["objetivos"]
            .apply(lambda x: x[0] * -1)
            .reset_index(drop="True")
        )
        df_final["Pontuacao_2"] = (
            df[["objetivos"]]
            .explode("objetivos")["objetivos"]
            .apply(lambda x: x[1] if len(x) > 1 else math.inf)
            .reset_index(drop="True")
        )
    else:
        df_final["Pontuacao"] = (
            df[["objetivos"]]
            .explode("objetivos")["objetivos"]
            .apply(lambda x: x[0] * -1)
            .reset_index(drop="True")
        )

    df_final["constraints"] = (
        df[["constraints"]].explode("constraints").reset_index(drop=True)["constraints"]
    )
    df_final["objetivos_penalizados"] = (
        df[["objetivos_penalizados"]]
        .explode("objetivos_penalizados")["objetivos_penalizados"]
        .apply(lambda x: x[0])
        .reset_index(drop="True")
    )
    df_final["viavel"] = (
        df[["viavel"]].explode("viavel").reset_index(drop=True)["viavel"]
    )
    parametros = df[["parameters"]].explode("parameters")["parameters"].to_list()
    variaveis = ["Area", "CL", "CD", "Massa_Vazia", "a", "b", "c", "d"]

    #     if len(parametros[0]) > 10:
    #         [variaveis.append(f"Chord_{i}") for i in range(1,12)]
    #     # Ordem dos coef pode estar errada
    #     if len(parametros[0])==18:
    #         [param.insert(7,0) for param in parametros]

    #     if len(parametros[0])==17:
    #         [param.insert(6,0) for param in parametros]
    #         [param.insert(6,0) for param in parametros]

    #     if len(parametros[0]) < 10:
    #         variaveis.append("extra")
    #         for i in range(0, len(parametros)):
    #             if len(parametros[i]) >10:
    #                 parametros[i] = [0]*9

    #     resultados = pd.DataFrame(parametros, columns= variaveis)
    #     df_final = pd.concat([df_final, resultados], axis=1)

    variaveis = ["Area", "CL", "CD", "Massa_Vazia"]
    resultados = pd.DataFrame(
        df[["parameters"]].explode("parameters")["parameters"].to_list(),
        columns=variaveis,
    )
    df_final = pd.concat([df_final, resultados], axis=1)
    df = df_final
    df["Envergadura_2"] = df["Envergadura_1"] + df["Envergadura_2"]
    df["Envergadura_3"] = df["Envergadura_2"] + df["Envergadura_3"]

    df["Corda_2"] = df["Corda_1"] - df["Corda_2"]
    df["Corda_3"] = df["Corda_2"] - df["Corda_3"]
    df["Corda_4"] = df["Corda_3"] - df["Corda_4"]

    df["Offset_2"] = df["Offset_1"] + df["Offset_2"]
    df["Offset_3"] = df["Offset_2"] + df["Offset_3"]

    return df


def animacao_pareto(execution=1) -> None:
    """
    Gera a animação da fronteira de pareto, para otimização multiobjetivo. A animação é criada na pasta "pareto".

    :param execution: Qual o numero da execução desejada, defaults to 1
    :type execution: int, optional
    """    
    df = ler_logs(f"tipo=4/Journal_aero_4_20_300_R{execution}")
    df = df[df["viavel"] == 0]
    for i in range(0, 300):
        ultima = df[df["Geracao"] == i]
        plt.scatter(ultima.Pontuacao_1, ultima.Pontuacao_2)
        plt.xlim(80, 230)
        plt.ylim(0, 35)
        plt.savefig(f"../pareto/quadro_{i}.jpeg")
        plt.close()

    # Video
    video_name = f"../pareto/pareto_R{execution}" + ".mp4"
    images = [img for img in os.listdir("../pareto") if img.endswith(".jpeg")]
    # print (images)
    frame = cv2.imread(f"../pareto/{images[0]}")
    height, width, layers = frame.shape

    df = pd.DataFrame([image.split("_")[1] for image in images], images).reset_index()
    df.columns = ["file", "quadro"]
    df["quadro"] = df["quadro"].str.strip(".jpeg").astype(int)
    df = df.sort_values(by=["quadro"])
    df["file"] = "../pareto/" + df["file"]

    images = list(df["file"])

    fps = 25
    video = cv2.VideoWriter(video_name, 0, fps, (width, height))

    for image in images:
        video.write(cv2.imread(image))

    cv2.destroyAllWindows()
    video.release()


def render_mpl_table(
    data,
    col_width=3.0,
    row_height=0.625,
    font_size=14,
    header_color="#40466e",
    row_colors=["#f1f1f2", "w"],
    edge_color="w",
    bbox=[0, 0, 1, 1],
    header_columns=0,
    ax=None,
    **kwargs,
    ):
    """
    Renderiza um Dataframe
    """
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array(
            [col_width, row_height]
        )
        fig, ax = plt.subplots(figsize=size)
        ax.axis("off")

    mpl_table = ax.table(
        cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs
    )

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight="bold", color="w")
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0] % len(row_colors)])
    return ax


def plot_asa(
    geo, position=[1, 1, 1], figure=0, grade=True, color="black", sections=False
    ):
    """
    Recebe o "df.iloc[x]"

    """

    #     pontuacao = geo[8]
    #     georacao = geo[7]
    geo = list(geo)  # [0:10]

    envs = geo[0:3]

    # Isso é para o sem interpolação
    if len(geo) > 21:
        cordas = geo[20:]
    else:
        cordas = geo[3:7]

    offsets = []

    envs_new = []
    for i in range(0, len(cordas)):
        envs_new.append(i * (max(envs) * 2) / (2 * (len(cordas) - 1)))

    envs = envs_new

    for i in range(0, len(cordas)):
        if i == 0:
            offsets.append(0)
        else:
            offsets.append((cordas[0] - cordas[i]) / 2)

    if figure == 0:
        fig = plt.figure()
    else:
        fig = figure

    ax = fig.add_subplot(*position, aspect="equal")

    if sections == False:
        x = [0, envs[0], envs[1], envs[2], envs[2], envs[1], envs[0], 0]
        y = [
            0,
            offsets[0],
            offsets[1],
            offsets[2],
            offsets[2] + cordas[-1],
            offsets[1] + cordas[-2],
            offsets[0] + cordas[-3],
            cordas[-4],
        ]

        # Cobem
        x = envs + envs[::-1]
        y = offsets + list(np.sum([offsets[::-1], cordas[::-1]], axis=0))

        ax.add_patch(patches.Polygon(xy=list(zip(x, y)), fill=False, color="black"))

    else:
        # Seção 1
        x = [0, envs[0], envs[0], 0]
        y = [0, offsets[0], offsets[0] + cordas[-3], cordas[-4]]
        ax.add_patch(patches.Polygon(xy=list(zip(x, y)), fill=False))

        # Seção 2
        x = [envs[0], envs[1], envs[1], envs[0]]
        y = [offsets[0], offsets[1], offsets[1] + cordas[-2], offsets[0] + cordas[-3]]
        ax.add_patch(patches.Polygon(xy=list(zip(x, y)), fill=False))

        # Seção 3
        x = [envs[1], envs[2], envs[2], envs[1]]
        y = [offsets[1], offsets[2], offsets[2] + cordas[-1], offsets[1] + cordas[-2]]
        ax.add_patch(patches.Polygon(xy=list(zip(x, y)), fill=False))

    if color != 0:
        ax.add_patch(patches.Polygon(xy=list(zip(x, y)), fill=True, color=color))

    x = [value * -1 for value in x]

    ax.add_patch(patches.Polygon(xy=list(zip(x, y)), fill=False))

    if color != 0:
        ax.add_patch(patches.Polygon(xy=list(zip(x, y)), fill=True, color=color))

    plt.xlim(min(x) * -1.2, min(x) * 1.2)
    plt.ylim(-0.3, max(y) * 1.3)

    if sections:
        plt.xlim(0, min(x) * 1.2 * -1)

    if grade:
        plt.title(f"")

    else:
        plt.axis("off")


#     plt.show()
#     return (ax)


def checa_sobrevivencia(df):
    df["Sobreviveu"] = ""
    posicao = 0
    for i in range(0, len(df) - 1):
        for x, individuo in enumerate(
            [list(linha[:10]) for linha in df[df["Geracao"] == i].values]
        ):
            #             filename = df[df["Geracao"] == i].values[x][-3]
            if individuo in [
                list(linha[:10]) for linha in df[df["Geracao"] == i + 1].values
            ]:
                #                 df.loc[df["File"]==filename,"Sobreviveu"] = "Sim"
                df.loc[posicao, "Sobreviveu"] = "Sim"
            else:
                df.loc[posicao, "Sobreviveu"] = "Não"
            posicao += 1
    return df


def animacao(df, file="animacao_geracoes"):
    """
    Cria uma animação em vídeo a partir das várias gerações da otimização. 

    :param df: Dataframe com os indivíduos e suas características.
    :type df: Dataframe.
    :param file: Nome da animação resultante, defaults to "animacao_geracoes"
    :type file: str, optional
    """    
    #     df = checa_sobrevivencia(df)
    directory = "./plot/"
    linhas = 8
    colunas = 5
    for geracao in range(0, df["Geracao"].nunique() - 1):
        f = plt.figure(figsize=(15, 8))
        atual = df[df["Geracao"] == geracao].reset_index(drop=True)
        for i in range(1, len(atual) + 1):
            plot_asa(atual.iloc[i - 1], [linhas, colunas, i], f, grade=False)

        plt.savefig(f"{directory}geracao_{geracao}_0.jpeg", transparent=False)

        f = plt.figure(figsize=(15, 8))
        for i in range(1, len(atual) + 1):
            if atual.loc[i - 1, "Sobreviveu"] == "Sim":
                plot_asa(
                    atual.iloc[i - 1],
                    [linhas, colunas, i],
                    f,
                    grade=False,
                    color="green",
                )

            elif atual.loc[i - 1, "Sobreviveu"] == "Não":
                plot_asa(
                    atual.iloc[i - 1],
                    [linhas, colunas, i],
                    f,
                    grade=False,
                    color="firebrick",
                )

        plt.savefig(f"{directory}geracao_{geracao}_1.jpeg", transparent=False)

    # Video
    video_name = directory + file + ".mp4"
    images = [img for img in os.listdir(directory) if img.endswith(".jpeg")]
    frame = cv2.imread(os.path.join(directory, images[0]))
    height, width, layers = frame.shape

    df = pd.DataFrame([image.split("_")[1:3] for image in images], images).reset_index()
    df.columns = ["file", "geracao", "tipo"]
    df["geracao"] = df["geracao"].astype(int)
    df["tipo"] = df["tipo"].str[0].astype(int)
    df = df.sort_values(by=["geracao", "tipo"])
    images_formatos = list(df[df["tipo"] == 0]["file"])
    images_cores = list(df[df["tipo"] == 1]["file"])
    images = list(df["file"])

    fps = 5
    video = cv2.VideoWriter(video_name, 0, fps, (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join(directory, image)))

    cv2.destroyAllWindows()
    video.release()


def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)

    return allFiles


def criar_dataframe_historicos():
    """

    ./Resultados\grau=0\Cobem_poly_0_20_300_R1.txt


    Cria o dataframe com todos os logs de históricos gerados pelo MOGA.
    Procura em toda a pasta de resultados por arquivos .txt nesse formato e joga em um Dataframe.
    """
    df = pd.DataFrame(
        columns=["Tempo", "Historicas", "Novas", "Bloqueadas", "Grau", "Rodada", "File"]
    )
    # df.columns = ["Tempo", "Historicas", "Novas", "Bloqueadas", "Grau", "Rodada", "File"]
    listOfFiles = getListOfFiles("./Resultados")
    for file in listOfFiles:
        if file.endswith(".txt"):
            with open(file, "r") as result:
                grau = re.findall("grau=\d", file)[0][-1]
                rodada = re.findall("R\d+", file)[0][1:]
                tudo = result.readlines()[1:]
                tudo.append(grau)
                tudo.append(rodada)
                tudo.append(file)

                df2 = pd.DataFrame(tudo).T
                df2.columns = [
                    "Tempo",
                    "Historicas",
                    "Novas",
                    "Bloqueadas",
                    "Grau",
                    "Rodada",
                    "File",
                ]
                df = pd.concat([df, df2])

    df["Tempo"] = df["Tempo"].apply(lambda x: float(x.split()[2]))
    df["Historicas"] = df["Historicas"].apply(lambda x: float(x.split()[4]))
    df["Novas"] = df["Novas"].apply(lambda x: float(x.split()[4]))
    df["Bloqueadas"] = df["Bloqueadas"].apply(lambda x: float(x.split()[4]))
    df = df.reset_index(drop=True)
    df["File"] = df["File"].apply(lambda x: x.split("\\")[-1].split(".")[-2])
    df.to_csv("historicos.csv")


def gerar_relatorios():
    """
    Gera os relatórios em PDF com todas os principais resultados de uma execução. 
    """    
    maximos_totais = pd.DataFrame()

    for j in range(0, 4):
        for i in range(1, 6):
            file = f"Journal_aero_{j}_20_300_R{i}"
            grau = j
            path = f"tipo={grau}/" + file
            df = ler_logs(path)

            df = df[df["viavel"] == 0]
            maximo = df.sort_values(["Geracao", "Pontuacao"]).groupby("Geracao").last()
            maximo.to_csv(f"../maximos/{file}_max_payload.csv")

            maximo = maximo[["Pontuacao"]]
            maximo["File"] = file
            maximo["Execucao"] = file.split("_")[-1]
            maximos_totais = pd.concat([maximos_totais, maximo])

            ultima = df[df["Geracao"] == 299]

            # ultima = ultima[['Envergadura_1', 'Envergadura_2', 'Envergadura_3', 'Corda_1', 'Corda_2',
            #        'Corda_3', 'Corda_4', 'Pontuacao', 'Area', 'CL', 'CD', 'Massa_Vazia']]

            ultima = ultima[
                [
                    "Envergadura_1",
                    "Envergadura_2",
                    "Envergadura_3",
                    "Corda_1",
                    "Corda_2",
                    "Corda_3",
                    "Corda_4",
                    "Pontuacao",
                ]
            ]

            # Imagens

            # Dataframe
            for coluna in ultima.columns:
                ultima[coluna] = ultima[coluna].apply(lambda x: str(x)[:4])

            ultima = ultima.rename(
                columns={
                    "Envergadura_1": "Env_1",
                    "Envergadura_2": "Env_2",
                    "Envergadura_3": "Env_3",
                }
            )

            if grau == 4:
                ultima = ultima.sort_values(
                    ["Pontuacao_1", "Pontuacao_2"], ascending=False
                )

            ultima = ultima.head(20)

            render_mpl_table(ultima, header_columns=0, col_width=2.0)
            plt.savefig("ultima.png")
            plt.close()

            # Melhor asa
            plot_asa(df.loc[11999])
            plt.savefig("melhor.png")
            plt.close()

            # Plotar tudo
            # for i in range(0, len(ultima)):
            #     plot_asa(ultima.iloc[i])

            # Payload Generation
            if grau != 4:
                plt.figure(figsize=(10, 8))
                viavel = df[df["viavel"] == 0]
                viavel.groupby("Geracao").max()["Pontuacao"].plot()
                nome = "payload_generation"
                plt.title("Journal - Aero")
                plt.xlabel("Generation")
                plt.ylabel("Pontuation")
                plt.ylim(15, 19.5)
                plt.savefig(f"{nome}.png")
                plt.close()

            # Payload Area

            if grau != 4:
                sns.set(font_scale=1.3)
                plt.figure(figsize=(10, 8))
                sns.scatterplot(
                    data=df, x="Area", y="Pontuacao", alpha=1, palette=["black"]
                )

                plt.xlabel("Wing Surface Area ($\mathregular{m^{2}}$)")
                plt.ylabel("Pontuation")
                plt.title("Journal - Aero")

                _ = plt.xlim(0, 3.5)
                _ = plt.ylim(5, 22)
                plt.savefig("payload_area.png")
                plt.close()

            # Animacao
            # df = checa_sobrevivencia(df)
            # animacao(df)

            # Relatório
            pdf = fpdf.FPDF()
            pdf.add_page()
            pdf.set_font("arial", "B", 30)
            pdf.cell(60)
            pdf.cell(75, 10, f"{file}", 0, 2, "C")
            pdf.set_font("arial", "B", 11)
            pdf.cell(75, 10, "Ultima Geração", 0, 2, "C")
            pdf.cell(90, 10, "", 0, 2, "C")
            pdf.cell(-55)
            # columNamelist = materias.columns
            # for column in columNamelist:
            #     pdf.cell(35, 10, column, 1, 0, "C")
            # pdf.cell(-140)
            pdf.image("ultima.png", x=0, y=None, w=200, h=0, type="", link="")
            pdf.image(
                "payload_generation.png", x=0, y=None, w=200, h=0, type="", link=""
            )
            pdf.image("payload_area.png", x=0, y=None, w=200, h=0, type="", link="")
            pdf.cell(60)
            pdf.cell(75, 10, "Melhor Asa", 0, 2, "C")
            pdf.cell(-60)
            pdf.image("melhor.png", x=0, y=None, w=200, h=0, type="", link="")

            pdf.output(f"./Resultados/tipo={grau}/{file}.pdf", "F")

    maximos_totais.to_csv(f"maximos/max_compilado.csv")


def cria_arquivo_stats():
    """
    Desisti disso por enquanto
    """
    df = pd.read_csv("historicos.csv", index_col=0)
    df["Total"] = df.apply(lambda x: x["Novas"] + x["Bloqueadas"], axis=1)
    df["Media Viavel"] = df.apply(lambda x: x["Novas"] / x["Total"], axis=1)
    df["Media Inviavel"] = df.apply(lambda x: x["Bloqueadas"] / x["Total"], axis=1)

    df = df.groupby("Grau").mean()

    df.index = ["Segmented", "Linear", "Quadratic", "Cubic"]
    df = df.reset_index()
    df = df.rename(columns={"index": "Model"})
    df = df.drop("Tempo", axis=1)

    maxi = pd.read_csv("./maximos/max_compilado.csv")
    maxi = maxi.groupby("File").agg({"Pontuacao": ["mean", "max", "std"]}).reset_index()
    maxi = pd.concat(
        [maxi[["File"]], maxi["Pontuacao"]], axis=1
    )  # .rename(columns = {"(File,)": "File"})
    maxi.columns = ["File", "mean", "max", "std"]
    maxi["Grau"] = maxi["File"].apply(lambda x: x.split("_")[2])
    maxi = maxi.groupby("Grau").mean()

    df["Maximum payload [kg]"] = maxi["max"]
    df["Mean payload [kg]"] = maxi["mean"]
    df["Standard deviation of payload [kg]"] = maxi["std"]

    df = df[
        [
            "Model",
            "Maximum payload [kg]",
            "Mean payload [kg]",
            "Standard deviation of payload [kg]",
            "Media Viavel",
            "des_via",
            "Media Inviavel",
            "des_inv",
            "med_tot",
            "des_tot",
        ]
    ]

    df.to_csv("stats.csv")
    return df
