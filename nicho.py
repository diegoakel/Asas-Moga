import Modelo
import math
from typing import List, Union

def filtra_nicho(new_solution, rank, matriz_function, n_rank) -> List:
    maximos_f, minimos_f = calcula_max_min(matriz_function)
    rank = filtra_limites(matriz_function, rank)
    while len(new_solution) > Modelo.pop_size:
        temp = pior_nicho(new_solution, rank, matriz_function, n_rank, maximos_f, minimos_f)
        rank[new_solution[temp]] = math.inf
        matriz_function[new_solution[temp]] = [math.inf for i in range(0, Modelo.no_objetivos)]
        new_solution = [i for x, i in enumerate(new_solution) if x != temp]
    return new_solution


def pior_nicho(new_solution, rank, matriz_function, n_rank, maximos_f, minimos_f) -> int:
    if n_rank == 0:
        i_temp = pior_nicho_rank_0(new_solution, rank, matriz_function, n_rank, maximos_f, minimos_f)
    else:
        i_temp = pior_nicho_dominated(new_solution, rank, matriz_function, n_rank, maximos_f, minimos_f)
    return i_temp


def pior_nicho_rank_0(new_solution, rank, matriz_function, n_rank, maximos_f, minimos_f) -> int:
    #print(f"Rank calculado na fronteira: {n_rank}")
    nicho = nicho_pop_rank_0(matriz_function, rank, n_rank, maximos_f, minimos_f)
    i_temp = find_first_rank_n(rank, new_solution, n_rank)
    for i in range(0, len(new_solution)):
        if (nicho[new_solution[i]] < nicho[new_solution[i_temp]]) and (rank[new_solution[i]] == n_rank):
            i_temp = i
    return i_temp


def pior_nicho_dominated(new_solution, rank, matriz_function, n_rank, maximos_f, minimos_f) -> int:
    #print(f"Rank calculado fora da fronteira: {n_rank}")
    nicho = nicho_pop_dominated(matriz_function, rank, n_rank, maximos_f, minimos_f)
    i_temp = find_first_rank_n(rank, new_solution, n_rank)
    for i in range(0, len(new_solution)):
        if (nicho[new_solution[i]] > nicho[new_solution[i_temp]]) and (rank[new_solution[i]] == n_rank):
            i_temp = i
    return i_temp


def calcula_subnicho_rank_0(matriz_function, rank, p, maximos_f, minimos_f) -> float:
    num_nicho = 0
    for i in range(0, len(matriz_function)):
        if (rank[i] == 0) or (rank[i] == -1 * math.inf):
            if i != p:
                if Distancia_Function(matriz_function, p, i, maximos_f, minimos_f) < Modelo.raio_nicho:
                    num_nicho = num_nicho + 1
    return num_nicho

def calcula_nicho_rank_0(matriz_function, rank, p, maximos_f, minimos_f) -> float:
    result = 0
    for i in range(0, len(matriz_function)):
        if (i != p):
            if (rank[i] == 0) or (rank[i] == -1 * math.inf):
                dist_temp = Distancia_Function(matriz_function, p, i, maximos_f, minimos_f)
                if dist_temp < Modelo.raio_nicho:
                    result = result + dist_temp
    return result

def calcula_nicho_dominated(matriz_function, rank, p, maximos_f, minimos_f) -> float:
    dist_temp = 0
    for i in range(0, len(matriz_function)):
        if (i != p):
            if (rank[i] == 0) or (rank[i] == -1 * math.inf):
                dist_temp = dist_temp + Distancia_Function(matriz_function, p, i, maximos_f, minimos_f)
    return dist_temp


def nicho_pop_rank_0(matriz_function, rank, n_rank, maximos_f, minimos_f) -> List:
    nicho = [math.inf for i in range(0, len(matriz_function))]
    subnicho = subnicho_pop_rank_0(matriz_function, rank, n_rank, maximos_f, minimos_f) 
    for p in range(0, len(matriz_function)):
        if (rank[p] == n_rank) and (subnicho[p] == max(subnicho)):
            nicho[p] = calcula_nicho_rank_0(matriz_function, rank, p, maximos_f, minimos_f)
    return nicho


def subnicho_pop_rank_0(matriz_function, rank, n_rank, maximos_f, minimos_f) -> List:
    subnicho = [-1 * math.inf for i in range(0, len(matriz_function))]
    for p in range(0, len(matriz_function)):
        if (rank[p] == n_rank):
            subnicho[p] = calcula_subnicho_rank_0(matriz_function, rank, p, maximos_f, minimos_f)
    return subnicho


def nicho_pop_dominated(matriz_function, rank, n_rank, maximos_f, minimos_f) -> List:
    nicho = [-1 * math.inf for i in range(0, len(matriz_function))]
    for p in range(0, len(matriz_function)):
        if rank[p] == n_rank:
            nicho[p] = calcula_nicho_dominated(matriz_function, rank, p, maximos_f, minimos_f)
    return nicho


def filtra_limites(matriz_function, rank) -> list:
    limits_pareto = find_limits_pareto(matriz_function, rank)
    for i in range(0, len(limits_pareto)):
        rank[limits_pareto[i]] = -1 * math.inf

    return rank


def calcula_max_min(matriz_function) -> List:
    maximos = [-1 * math.inf] * len(matriz_function[0])
    minimos = [1 * math.inf] * len(matriz_function[0])

    for i in range(0, len(matriz_function)):
        for j in range(0, len(matriz_function[i])):

            if (maximos[j] < matriz_function[i][j]) and (abs(matriz_function[i][j]) != math.inf):
                maximos[j] = matriz_function[i][j]

            if (minimos[j] > matriz_function[i][j]) and (abs(matriz_function[i][j]) != math.inf):
                minimos[j] = matriz_function[i][j]

    return maximos, minimos


def find_first_rank_n(rank, new_solution, n_rank) -> float:
    for i in range(0, len(new_solution)): 
        if rank[new_solution[i]] == n_rank:
            return i
    return 0

def find_first_rank_0(rank) -> float:
    for i in range(0, len(rank)): 
        if rank[i] == 0:
            return i
    return 0    

def find_limits_pareto(matriz_function, rank) -> List:
    first_mono = find_first_rank_0(rank)
    i_opt_mono = [first_mono] * len(matriz_function[0])
    
    for i in range(0, len(matriz_function)):
        for j in range(0, len(matriz_function[i])):
            if rank[i] == 0:
                if (matriz_function[i_opt_mono[j]][j] > matriz_function[i][j]):
                    i_opt_mono[j] = i

    return i_opt_mono



def Distancia_Function(matriz_function, p, q, maximos_f, minimos_f) -> float:
    temp = 0
    for i in range(0, len(matriz_function[p])):
        f1_ad = (matriz_function[p][i] - minimos_f[i]) 
        f2_ad = (matriz_function[q][i] - minimos_f[i])
        if maximos_f[i] - minimos_f[i] > 0:
            f1_ad = f1_ad / (maximos_f[i] - minimos_f[i])
            f2_ad = f2_ad / (maximos_f[i] - minimos_f[i])
        temp = temp + (f1_ad - f2_ad) ** 2
    return temp ** 0.5