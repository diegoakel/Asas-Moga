import analise
import constantes

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

#parametro otimização
pop_size = 20
taxa_mutacao = 0.04
max_gen = 300
porcentagem_viavel_primeira_geracao = 0.5
tolerancia_nova_analise = 0

#Modelo do problema
no_objetivo = 1
no_restricoes = 4
no_parameters = 4

# Env1, Env2, Env3, Chord0, Chord1, Chord2, Chord3, offset1, offset2, offset3
x_res = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
x_min = [delta_envergadura_minima, delta_envergadura_minima, delta_envergadura_minima, corda_fuselagem_minimo, 0, 0, 0, 0, 0 ,0]## x = deadrise, LCG
x_max = [2, 2, 2, corda_fuselagem_maxima, 0.15, 0.15, 0.15, 0.25, 0.25, 0.25]
f_sinal = [constantes.maximizar] # "-" é maximizar e "+" é minimizar
f_pen = [1000, 10000, 10000, 10000] ## f1, f2
g_limite = [envergadura_maxima, corda_minima, corda_minima, corda_ponta_minima] ## g1, g2
g_sinal = [constantes.menor_que, constantes.maior_que, constantes.maior_que, constantes.maior_que] ## negativo < lim; positivo > lim

# Labels
nome_otimizacao = f"Relativo_{pop_size}_{max_gen}_MaxPontuacao_R5"


def Avalia_Individuo_Viavel(individuo, n, gen_no):
   objective = []
   constraint = []
   
   constraint.append(analise.retorna_envergadura(*fake_x(individuo[n])))
   constraint.append(analise.retorna_corda_1(*fake_x(individuo[n])))
   constraint.append(analise.retorna_corda_2(*fake_x(individuo[n])))  
   constraint.append(analise.retorna_corda_ponta(*fake_x(individuo[n])))

   objective.append(f_sinal[0] * analise.calcula_carga_paga(*fake_x(individuo[n])))

   parameters = analise.retorna_parametros()

   return objective, constraint, parameters


def pre_checagem(vetor_x):
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
   fake_env = [vetor_x[0], vetor_x[0]+ vetor_x[1], vetor_x[0] + vetor_x[1] + vetor_x[2]]
   fake_corda = [vetor_x[3], vetor_x[3] - vetor_x[4], vetor_x[3] - vetor_x[4] - vetor_x[5], vetor_x[3]- vetor_x[4] - vetor_x[5] - vetor_x[6]]
   fake_offset = [vetor_x[7], vetor_x[7] + vetor_x[8], vetor_x[7] + vetor_x[8] + vetor_x[9]]

   return fake_env, fake_corda, fake_offset

