import analise
import constantes
from typing import List, Union

# Parametros Ambientais
g = 9.81
rho_ar = 1.225
mi_solo = 0.025

# Parametros do problema
delta_envergadura_minima = 0.3
envergadura_maxima = 4.2
corda_ponta_minima = 0.05
corda_minima = 0.05
corda_fuselagem_maxima = 1
corda_fuselagem_minimo = 0.1

# Parâmetros de análise
comprimento_pista_maxima = 90
comprimento_elemento_env = 0.05
num_elementos_corda = 20
a = -0.0126
b = -0.5248
c = 40.0248
alfa_stol = 13.5
fator_corretivo = 1.09

# parametro otimização
pop_size = 20
taxa_mutacao = 0.04
max_gen = 300
porcentagem_viavel_primeira_geracao = 0.5
tolerancia_nova_analise = 0
raio_nicho = 0.15

# Modelo do problema
no_objetivos = 2
no_restricoes = 4
no_parameters = 4
tipo_problema = 0

# Env1, Env2, Env3, Chord0, Chord1, Chord2, Chord3, offset1, offset2, offset3
x_res = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
x_min = [
    delta_envergadura_minima,
    delta_envergadura_minima,
    delta_envergadura_minima,
    corda_fuselagem_minimo,
    0,
    0,
    0,
    0,
    0,
    0,
]  ## x = deadrise, LCG
x_max = [2, 2, 2, corda_fuselagem_maxima, 0.15, 0.15, 0.15, 0.25, 0.25, 0.25]
f_sinal = [constantes.maximizar, constantes.minimizar]  # "-" é maximizar e "+" é minimizar
f_pen = [1000, 10000, 10000, 10000]  ## f1, f2
g_limite = [
    envergadura_maxima,
    corda_minima,
    corda_minima,
    corda_ponta_minima,
]  ## g1, g2
g_sinal = [
    constantes.menor_que,
    constantes.maior_que,
    constantes.maior_que,
    constantes.maior_que,
]  ## negativo < lim; positivo > lim

# Labels
# nome_otimizacao = f"Relativo_{pop_size}_{max_gen}_MaxPontuacao_R5"


def Avalia_Individuo_Viavel(individuo, n, gen_no):
    """
    Caso o indivíduo seja viável, essa função avalia o indivíduo através do módulo de analise.

    As diferentes funções objetivos são calculadas aqui.

    :param individuo: População
    :type individuo: List[List[float]]
    :param n: Index do indivíduo na população.
    :type n: int
    :param gen_no: Número da geração.
    :type gen_no: int
    :return: Valores de objetivo, parametros e restrições.
    :rtype: List[float]
    """    
    objective = []
    constraint = []

    constraint.append(analise.retorna_envergadura(*fake_x(individuo[n])))
    constraint.append(analise.retorna_corda_1(*fake_x(individuo[n])))
    constraint.append(analise.retorna_corda_2(*fake_x(individuo[n])))
    constraint.append(analise.retorna_corda_ponta(*fake_x(individuo[n])))

    if tipo_problema == 0:
        objective.append(f_sinal[0] * analise.calcula_carga_paga(*fake_x(individuo[n])))

    elif tipo_problema == 1:
        objective.append(f_sinal[0] * analise.calcula_lift(*fake_x(individuo[n])))

    elif tipo_problema == 2:
        objective.append(f_sinal[1] * analise.calcula_drag(*fake_x(individuo[n])))

    elif tipo_problema == 3:
        objective.append(f_sinal[0] * analise.calcula_eficiencia(*fake_x(individuo[n])))

    elif tipo_problema == 4:
        objective.append(f_sinal[0] * analise.calcula_lift(*fake_x(individuo[n])))
        objective.append(f_sinal[1] * analise.calcula_drag(*fake_x(individuo[n])))

    parameters = analise.retorna_parametros()

    return objective, constraint, parameters


def pre_checagem(vetor_x) -> int:
    """
    Verifica se o vetor x está dentro dos limites.

    :param vetor_x: Indivíduo a ser checado.
    :type vetor_x: List[float]
    :return: Viabilidade do indivíduo. 1 ou 0.
    :rtype: int
    """    
    if analise.retorna_envergadura(*fake_x(vetor_x)) > envergadura_maxima:
        return constantes.solucao_inviavel

    if analise.retorna_corda_1(*fake_x(vetor_x)) < corda_minima:
        return constantes.solucao_inviavel

    if analise.retorna_corda_2(*fake_x(vetor_x)) < corda_minima:
        return constantes.solucao_inviavel

    if analise.retorna_corda_ponta(*fake_x(vetor_x)) < corda_ponta_minima:
        return constantes.solucao_inviavel

    return constantes.solucao_viavel


def fake_x(vetor_x):
    """
    Cria o fake_vetor_x, que são as listas de geometria.

    :param vetor_x: Indivíduo.
    :type vetor_x: List[float]
    :return: Listas de valores de geometria, corda, offset e envergadura.
    :rtype: List[float]
    """    
    fake_env = [
        vetor_x[0],
        vetor_x[0] + vetor_x[1],
        vetor_x[0] + vetor_x[1] + vetor_x[2],
    ]
    fake_corda = [
        vetor_x[3],
        vetor_x[3] - vetor_x[4],
        vetor_x[3] - vetor_x[4] - vetor_x[5],
        vetor_x[3] - vetor_x[4] - vetor_x[5] - vetor_x[6],
    ]
    fake_offset = [
        vetor_x[7],
        vetor_x[7] + vetor_x[8],
        vetor_x[7] + vetor_x[8] + vetor_x[9],
    ]

    return fake_env, fake_corda, fake_offset