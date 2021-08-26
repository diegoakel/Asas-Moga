import pandas as pd
import Modelo
# import apoio

def Evolucao_completada(pop_new):
    print("Evolução finalizada.")
#    for i in range(0, pop_size):
#         print("Envergadura:", pop_new[i][0] , pop_new[i][1], pop_new[i][2],"Cordas:", pop_new[i][3],pop_new[i][4],pop_new[i][5],pop_new[i][6],"Offsets:",pop_new[i][7],pop_new[i][8],pop_new[i][9])


def Individuo_Avaliado(gen_no, n, individuo, function_objective, function_constraint, function_objective_penalizado, function_viavel, parameters):
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
    global df_pareto
    global df_sem_filhos
    
    df = pd.DataFrame()
    df_pareto = pd.DataFrame()
    df_sem_filhos = pd.DataFrame()

    print(f"Otimização {label} iniciada.")


def Geracao_Iniciada(gen_no, pop_new):
    print(f"\nGeração {gen_no} iniciada.")
    pass


def Geracao_Finalizada(gen_no, pop_new, objetivos, constraints, objetivos_penalizados, viavel, parameters, rank):
    global df
    dados = [gen_no, pop_new, objetivos, constraints, objetivos_penalizados, viavel, parameters, rank]
    df2 = pd.DataFrame(dados).T
    df2.columns = ["gen_no", "pop_new", "objetivos", "constraints", "objetivos_penalizados", "viavel", "parameters", "rank"]
    df = pd.concat([df, df2])

def Geracao_Finalizada_Pareto(gen_no, pop_new, objetivos, constraints, objetivos_penalizados, viavel, parameters, rank):
    global df_pareto

    pop_new_temp = []
    objetivos_temp = []
    constraints_temp = []
    objetivos_penalizados_temp = []
    viavel_temp = []
    parameters_temp = []
    rank_temp = []

    for i in range(0, len(rank)):
        if rank[i] == 0:
            pop_new_temp.append(pop_new[i])
            objetivos_temp.append(objetivos[i])
            constraints_temp.append(constraints[i])
            objetivos_penalizados_temp.append(objetivos_penalizados[i])
            viavel_temp.append(viavel[i])
            parameters_temp.append(parameters[i])
            rank_temp.append(rank[i]) 
    
    dados = [gen_no, pop_new_temp, objetivos_temp, constraints_temp, objetivos_penalizados_temp, viavel_temp, parameters_temp, rank_temp]
    df2 = pd.DataFrame(dados).T
    df2.columns = ["gen_no", "pop_new", "objetivos", "constraints", "objetivos_penalizados", "viavel", "parameters", "rank"]
    df_pareto = pd.concat([df_pareto, df2])
    
def Geracao_Sem_Filhos(gen_no, pop_new, objetivos, constraints, objetivos_penalizados, viavel, parameters, rank):
    global df_sem_filhos

    pop_new_temp = []
    objetivos_temp = []
    constraints_temp = []
    objetivos_penalizados_temp = []
    viavel_temp = []
    parameters_temp = []
    rank_temp = []    

    for i in range(0, Modelo.pop_size):
        pop_new_temp.append(pop_new[i])
        objetivos_temp.append(objetivos[i])
        constraints_temp.append(constraints[i])
        objetivos_penalizados_temp.append(objetivos_penalizados[i])
        viavel_temp.append(viavel[i])
        parameters_temp.append(parameters[i])
        rank_temp.append(rank[i]) 

    dados = [gen_no, pop_new_temp, objetivos_temp, constraints_temp, objetivos_penalizados_temp, viavel_temp, parameters_temp, rank_temp]
    df2 = pd.DataFrame(dados).T
    df2.columns = ["gen_no", "pop_new", "objetivos", "constraints", "objetivos_penalizados", "viavel", "parameters", "rank"]
    df_sem_filhos = pd.concat([df_sem_filhos, df2])


def Otimizacao_Finalizada(path, label, total, cont_historico, cont_nova, cont_pre_check):
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
    df_pareto.to_csv(f"{completo}_pareto.csv")
    df_sem_filhos.to_csv(f"{completo}_sem_filhos.csv")
    # apoio.gerar_relatorio(label, completo)