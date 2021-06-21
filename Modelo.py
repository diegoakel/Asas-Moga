from os import environ
import analise
import constantes
import numpy as np

# Parametros Ambientais
g = 9.81
rho_ar = 1.225
mi_solo = 0.025

# Parametros do problema
delta_envergadura_minima = 0.3
envergadura_maxima = 4.2
corda_ponta_minima = 0.05
corda_minima = 0.05
corda_maxima = 1
corda_fuselagem_maxima = 1
corda_fuselagem_minimo = 0.1

# Parâmetros de análise
comprimento_elemento_env = 0.05 
comprimento_pista_maxima = 90
num_elementos_corda = 20
a = -0.0126
b = -0.5248
c = 40.0248
alfa_stol = 13.5
grau_interpolacao = 3
num_sections = 11

# Parametro otimização
pop_size = 20
taxa_mutacao = 0.04
max_gen = 300
porcentagem_viavel_primeira_geracao = 0.49
tolerancia_nova_analise = 0

#Modelo do problema
no_objetivo = 1
no_restricoes = 3
no_parameters = 4 + num_sections + (grau_interpolacao + 1)

# Env1, Env2, Env3, Chord0, Chord1, Chord2, Chord3
x_res = [3, 3, 3, 3, 3, 3, 3]
x_min = [delta_envergadura_minima, 2*delta_envergadura_minima, 3*delta_envergadura_minima, corda_fuselagem_minimo, corda_minima, corda_minima, corda_minima]
x_max = [2, 2.2, 2.4, corda_fuselagem_maxima, corda_maxima, corda_maxima, corda_maxima]
f_sinal = [constantes.maximizar]
f_pen = [1000, 10000, 10000] 
g_limite = [envergadura_maxima, delta_envergadura_minima, delta_envergadura_minima]
g_sinal = [constantes.menor_que, constantes.maior_que, constantes.maior_que] 

# Labels
nome_otimizacao = f"Cobem_poly_3_{pop_size}_{max_gen}"

def Avalia_Individuo_Viavel(individuo, n, gen_no):
   objective = []
   constraint = []

   objective.append(f_sinal[0] * analise.calcula_carga_paga(*fake_x(individuo[n])))

   constraint.append(analise.retorna_envergadura(*fake_x(individuo[n])))
   constraint.append(analise.retorna_delta_envergadura_2(*fake_x(individuo[n])))
   constraint.append(analise.retorna_delta_envergadura_3(*fake_x(individuo[n])))

   parameters = analise.retorna_parametros()

   return objective, constraint, parameters


def pre_checagem(vetor_x):
   if analise.retorna_envergadura(*fake_x(vetor_x)) > envergadura_maxima:
      return constantes.solucao_inviavel

   if analise.retorna_delta_envergadura_2(*fake_x(vetor_x)) < delta_envergadura_minima:
      return constantes.solucao_inviavel
   
   if analise.retorna_delta_envergadura_3(*fake_x(vetor_x)) < delta_envergadura_minima:
      return constantes.solucao_inviavel

   return constantes.solucao_viavel

def fake_x(vetor_x):
   fake_env = [vetor_x[0], vetor_x[1], vetor_x[2]]
   fake_corda = [vetor_x[3], vetor_x[4], vetor_x[5], vetor_x[6]]
   fake_offset = [0, 0, 0]

   return fake_env, fake_corda, fake_offset

def calcula_secoes(vetor_x, vetor_y):
   x = np.array([0, vetor_x[0], vetor_x[1], vetor_x[2]])
   y = np.array([vetor_y[0], vetor_y[1], vetor_y[2], vetor_y[3]])
   z = np.polyfit(x, y, grau_interpolacao)
   return z

def calcula_corda(env_x, coef_interpolation):
   if grau_interpolacao == 2:
      return coef_interpolation[0]*env_x**2 + coef_interpolation[1]*env_x + coef_interpolation[2]
   
   if grau_interpolacao == 3:
      return coef_interpolation[0]*env_x**3 + coef_interpolation[1]*env_x**2 + coef_interpolation[2]*env_x + coef_interpolation[3]
