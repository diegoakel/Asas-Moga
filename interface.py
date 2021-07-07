import pandas as pd

# import apoio


def Evolucao_completada(pop_new):
    print("Evolução finalizada.")


#    for i in range(0, pop_size):
#         print("Envergadura:", pop_new[i][0] , pop_new[i][1], pop_new[i][2],"Cordas:", pop_new[i][3],pop_new[i][4],pop_new[i][5],pop_new[i][6],"Offsets:",pop_new[i][7],pop_new[i][8],pop_new[i][9])


def Individuo_Avaliado(
    gen_no,
    n,
    individuo,
    function_objective,
    function_constraint,
    function_objective_penalizado,
    function_viavel,
    parameters,
):
    #  print("Envergadura: ", individuo[0] , individuo[1], individuo[2],"Cordas:", individuo[3],individuo[4],individuo[5],individuo[6],"Offsets:",individuo[7],individuo[8],individuo[9])
    #  print("Pontuacao penalizada: ", function_objective_penalizado[0])
    #  print("Pontuacao: ", function_objective[0])
    #  print("Inviavel: ", function_viavel)
    pass


def Elitismo_Aplicado(rank, new_solution):
    # print("\nrank:", rank)
    # print("\nNS:", new_solution)
    pass


def Otimizacao_Iniciada(label):
    global df
    df = pd.DataFrame()
    # df =  pd.DataFrame(columns=["gen_no", "pop_new", "objetivos", "constraints", "objetivos_penalizados", "viavel", "parameters"])
    print(f"Otimização {label} iniciada.")


def Geracao_Iniciada(gen_no, pop_new):
    print(f"\nGeração {gen_no} iniciada.")
    pass


# df =  pd.DataFrame(columns=["gen_no", "pop_new", "objetivos", "constraints", "objetivos_penalizados", "viavel", "parameters"])
def Geracao_Finalizada(
    gen_no, pop_new, objetivos, constraints, objetivos_penalizados, viavel, parameters
):
    global df
    dados = [
        gen_no,
        pop_new,
        objetivos,
        constraints,
        objetivos_penalizados,
        viavel,
        parameters,
    ]
    df2 = pd.DataFrame(dados).T
    df2.columns = [
        "gen_no",
        "pop_new",
        "objetivos",
        "constraints",
        "objetivos_penalizados",
        "viavel",
        "parameters",
    ]
    df = pd.concat([df, df2])


def Otimizacao_Finalizada(
    path, label, total, cont_historico, cont_nova, cont_pre_check
):
    completo = path + label
    path = completo + ".txt"

    with open(path, "w") as file:
        file.write(f"------------\n")
        file.write(f"Tempo total: {total} segundos \n")
        file.write(f"Total de análises históricas: {cont_historico} \n")
        file.write(f"Total de análises novas: {cont_nova} \n")
        file.write(f"Total de análises bloqueadas: {cont_pre_check} \n")

    print(f"Otimização {label} finalizada.")
    print(f"Tempo total: {total} segundos")
    print(f"Total de análises históricas: {cont_historico}")
    print(f"Total de análises novas: {cont_nova}")
    print(f"Total de análises bloqueadas: {cont_pre_check}")
    df.to_csv(f"{completo}.csv")

    # apoio.gerar_relatorio(label, completo)