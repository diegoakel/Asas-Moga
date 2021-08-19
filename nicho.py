import Modelo
import math
from typing import List, Union


def filtra_nicho(new_solution, rank, matriz_function, n_rank) -> List:
    """
    Não só essa função, mas a estratégia de Nicho em si serve para cuidar da disperção da fronteira de Pareto.
    Impedindo que fique muito concentrada em uma região e perca os limites extremos.

    :param new_solution: Novas soluções
    :type new_solution: List[int]
    :param rank: Rank das soluções
    :type rank: List[int]
    :param matriz_function: Funções objetivo
    :type matriz_function: List[List[float]]
    :param n_rank: Número de rank
    :type n_rank: int
    :return: Novas soluções filtradas
    :rtype: List[float]
    """

    maximos_f, minimos_f = calcula_max_min(matriz_function)
    while len(new_solution) > Modelo.pop_size:
        temp = pior_nicho(
            new_solution, rank, matriz_function, n_rank, maximos_f, minimos_f
        )
        # print(rank)
        # print(matriz_function)
        # print(new_solution)
        # print(temp)
        # a = input("Pausa")
        rank[new_solution[temp]] = math.inf
        matriz_function[new_solution[temp]] = [
            math.inf for i in range(0, Modelo.no_objetivo)
        ]
        new_solution = [i for x, i in enumerate(new_solution) if x != temp]

    return new_solution


def Distancia_Function(matriz_function, p, q, maximos_f, minimos_f) -> float:
    """
    Calcula a distância entre as funções objetivos de dois pontos da população.

    :param matriz_function: funções objetivo
    :type matriz_function: List[List[float]]
    :param p: Ponto A
    :type p: int
    :param q: Ponto B
    :type q: int
    :param maximos_f: Maximo das funções objetivo
    :type maximos_f: List[float]
    :param minimos_f: Mínimo das funções objetivo
    :type minimos_f: List[float]
    :return: Distância
    :rtype: float
    """
    temp = 0
    for i in range(0, len(matriz_function[p])):
        if (abs(matriz_function[p][i]) != math.inf) and (
            abs(matriz_function[q][i]) != math.inf
        ):
            f1_ad = (matriz_function[p][i] - minimos_f[i]) / (
                maximos_f[i] - minimos_f[i]
            )
            f2_ad = (matriz_function[q][i] - minimos_f[i]) / (
                maximos_f[i] - minimos_f[i]
            )
            temp = temp + (f1_ad - f2_ad) ** 2
    return temp ** 0.5


def pior_nicho(
    new_solution, rank, matriz_function, n_rank, maximos_f, minimos_f
) -> int:
    """
    Determina o indivíduo dominado a ser removido.

    :param new_solution: Novas soluções
    :type new_solution: List[int]
    :param rank: Rank das soluções
    :type rank: List[int]
    :param matriz_function: Funções objetivo
    :type matriz_function: List[List[float]]
    :param n_rank: Número de rank
    :type n_rank: int
    :param maximos_f: Maximo das funções objetivo
    :type maximos_f: List[float]
    :param minimos_f: Mínimo das funções objetivo
    :type minimos_f: List[float]
    :return: Posição do indivíduo a ser removido.
    :rtype: int
    """

    if n_rank == 0:
        i_temp = pior_nicho_rank_0(
            new_solution, rank, matriz_function, n_rank, maximos_f, minimos_f
        )

    else:
        i_temp = pior_nicho_dominated(
            new_solution, rank, matriz_function, n_rank, maximos_f, minimos_f
        )

    return i_temp


def pior_nicho_rank_0(
    new_solution, rank, matriz_function, n_rank, maximos_f, minimos_f
) -> int:
    """
    Determina o indivíduo a ser removido, dentro os indivíduos com rank 0.
    """
    nicho = nicho_pop_rank_0(matriz_function, rank, n_rank, maximos_f, minimos_f)
    i_temp = 0
    for i in range(0, len(new_solution)):
        if (nicho[new_solution[i]] < nicho[new_solution[i_temp]]) and (
            rank[new_solution[i]] == n_rank
        ):
            i_temp = i

    return i_temp


def pior_nicho_dominated(
    new_solution, rank, matriz_function, n_rank, maximos_f, minimos_f
) -> int:
    """
    Determina o indivíduo dominado a ser removido.
    """
    print(f"Rank calculado: {n_rank}")
    nicho = nicho_pop_dominated(matriz_function, rank, n_rank, maximos_f, minimos_f)
    i_temp = 0
    for i in range(0, len(new_solution)):
        if (nicho[new_solution[i]] > nicho[new_solution[i_temp]]) and (
            rank[new_solution[i]] == n_rank
        ):
            i_temp = i

    return i_temp


def calcula_max_min(matriz_function) -> List:
    """
    Cálcula o maximo e mínimo das funções objetivo

    :param matriz_function: funções objetivo
    :type matriz_function: List[List[float]]
    :return: Listas de máximos e mínimos das funções objetivos
    :rtype: List[float]
    """
    maximos = [-1 * math.inf] * len(matriz_function[0])
    minimos = [1 * math.inf] * len(matriz_function[0])

    for i in range(0, len(matriz_function)):
        for j in range(0, len(matriz_function[i])):

            if (maximos[j] < matriz_function[i][j]) and (
                abs(matriz_function[i][j]) != math.inf
            ):
                maximos[j] = matriz_function[i][j]

            if (minimos[j] > matriz_function[i][j]) and (
                abs(matriz_function[i][j]) != math.inf
            ):
                minimos[j] = matriz_function[i][j]

    return maximos, minimos


def calcula_nicho(matriz_function, rank, p, maximos_f, minimos_f) -> float:
    """
    Retorna a distância entre o individuo p e os indivíduos da fronteira de pareto.
    Somente para individuos no mesmo rank.

    :param matriz_function: funções objetivo
    :type matriz_function: List[List[float]]
    :param rank: Rank dos indivíduos
    :type rank: List[int]
    :param p: Ponto A
    :type p: int
    :param maximos_f: Maximo das funções objetivo
    :type maximos_f: List[float]
    :param minimos_f: Mínimo das funções objetivo
    :type minimos_f: List[float]
    :return: Distância
    :rtype: float
    """

    dist_temp = 0
    for i in range(0, len(matriz_function)):
        if (i != p) and (rank[i] == 0):
            dist_temp = dist_temp + Distancia_Function(
                matriz_function, p, i, maximos_f, minimos_f
            )

    return dist_temp


def nicho_pop_rank_0(matriz_function, rank, n_rank, maximos_f, minimos_f) -> List:
    """
    Calcular nicho já faz o algoritmo passar a ser NSGA-II.

    O nicho serve para impedir que a fronteira de Pareto fique muito concentrada em uma região, passando a ser
    mais dispersa.

    :param matriz_function: funções objetivo
    :type matriz_function: List[List[float]]
    :param rank: Rank dos indivíduos
    :type rank: List[int]
    :param maximos_f: Maximo das funções objetivo
    :type maximos_f: List[float]
    :param minimos_f: Mínimo das funções objetivo
    :type minimos_f: List[float]
    :return: Lista com nichos
    :rtype: List
    """
    nicho = [math.inf for i in range(0, len(matriz_function))]
    for p in range(0, len(matriz_function)):
        if rank[p] == n_rank:
            nicho[p] = calcula_nicho(matriz_function, rank, p, maximos_f, minimos_f)

    return nicho


def nicho_pop_dominated(matriz_function, rank, n_rank, maximos_f, minimos_f) -> List:
    """
    Calcular nicho já faz o algoritmo passar a ser NSGA-II.

    O nicho serve para impedir que a fronteira de Pareto fique muito concentrada em uma região, passando a ser
    mais dispersa.

    :param matriz_function: funções objetivo
    :type matriz_function: List[List[float]]
    :param rank: Rank dos indivíduos
    :type rank: List[int]
    :param maximos_f: Maximo das funções objetivo
    :type maximos_f: List[float]
    :param minimos_f: Mínimo das funções objetivo
    :type minimos_f: List[float]
    :return: Lista com nichos
    :rtype: List
    """
    nicho = [-1 * math.inf for i in range(0, len(matriz_function))]
    for p in range(0, len(matriz_function)):
        if rank[p] == n_rank:
            nicho[p] = calcula_nicho(matriz_function, rank, p, maximos_f, minimos_f)

    return nicho
