import math
import Modelo

historico_vetor_x = []
historico_objetivo = []
historico_constraint = []
historico_objective_penalizado = []
historico_viavel = []
historico_parameters = []

def adicionar_individuo(vetor_x, objective, constraint, objective_penalizado, viavel, parameters):
    historico_vetor_x.append(vetor_x)
    historico_objetivo.append(objective)
    historico_constraint.append(constraint)
    historico_objective_penalizado.append(objective_penalizado)
    historico_viavel.append(viavel)
    historico_parameters.append(parameters)

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
    return historico_vetor_x[n], historico_objetivo[n], historico_constraint[n], historico_objective_penalizado[n], historico_viavel[n], historico_parameters[n]
