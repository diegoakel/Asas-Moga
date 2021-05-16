from random import uniform as random
import os
import pandas as pd
from Asa import asa
import apoio # visualizações
import moga # genetico
import openpyxl
import analise


#parametro otimização
pop_size = 5 #20
taxa_mutacao = 0.04
max_gen = 1 #300

#Modelo do problema
no_objetivo = 1
no_restricoes = 0

# Env1, Env2, Env3, Chord0, Chord1, Chord2, Chord3, offset1, offset2, offset3
x_res = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
x_min = [0.2, 0.2, 0.2, 0.3, 0, 0, 0, 0, 0 ,0]## x = deadrise, LCG
x_max = [2,2,2, 0.5,0.15,0.15,0.15, 0.05, 0.05, 0.05]
f_pen = [] ## f1, f2
g_limite = [] ## g1, g2
g_sinal = [] ## negativo < lim; positivo > lim

def Evolucao_completada(pop_new):
   print("FINAL")
#    for i in range(0, pop_size):
#         print("Envergadura:", pop_new[i][0] , pop_new[i][1], pop_new[i][2],"Cordas:", pop_new[i][3],pop_new[i][4],pop_new[i][5],pop_new[i][6],"Offsets:",pop_new[i][7],pop_new[i][8],pop_new[i][9])

def Avalia_Individuo_Viavel(individuo, n):
   objective = [ ]
   constraint = [ ]

   objective.append(-1* analise.fake_analisa(individuo[n]))

   return objective, constraint


def Individuo_Avaliado(gen_no, n, individuo, function_objective, function_constraint, function_objective_penalizado):
    print("Envergadura: ", individuo[0] , individuo[1], individuo[2],"Cordas:", individuo[3],individuo[4],individuo[5],individuo[6],"Offsets:",individuo[7],individuo[8],individuo[9])
    print("Pontuacao: ", function_objective[0])   

def Elitismo_Aplicado(rank, new_solution):
   print("\nrank:", rank)
   print("\nNS:", new_solution)

def Nova_GeracaoIniciada(n, pop_new):
   print("\nGen nº:", n)