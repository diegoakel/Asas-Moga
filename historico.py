import math
import Modelo

historico_vetor_x = []
historico_objetivo = []
historico_constraint = []
historico_objective_penalizado = []
historico_viavel = []

def adicionar_individuo(vetor_x, function_objective, function_constraint, function_objective_penalizado, function_viavel):
    historico_vetor_x.append(vetor_x)
    historico_objetivo.append(function_objective)
    historico_constraint.append(function_constraint)
    historico_objective_penalizado.append(function_objective_penalizado)
    historico_viavel.append(function_viavel)


def calcular_distancia(vetor_x1, vetor_x2):
    soma = 0
    for i in range (0, len(vetor_x1)):
        soma = soma + ((vetor_x1[i] - vetor_x2[i])/(Modelo.x_max[i] - Modelo.x_min[i]))**2
    
    return math.sqrt(soma)


def procurar_individuo(vetor_x):
    for i in range (0, len(historico_viavel)):
        if calcular_distancia(vetor_x, historico_vetor_x[i]) <= Modelo.tolerancia_nova_analise:
            return i
        
    return -1
        

def retornar_individuo(n):
    return historico_vetor_x[n], historico_objetivo[n], historico_constraint[n], historico_objective_penalizado[n], historico_viavel[n]
