# Esse é o repositório aboluto.

import Moga_2020
import time

print ("Otimização iniciada.")

inicio = time.time()
pop_new = []
Moga_2020.Evolucao(pop_new)
fim = time.time()
total = fim-inicio

print (f"Tempo total: {total} segundos")

print (f"Total de análises históricas: {Moga_2020.cont_analise_historico[0]}")
print (f"Total de análises novas: {Moga_2020.cont_analise_nova[0]}")
print (f"Total de análises bloqueadas: {Moga_2020.cont_analise_pre_check[0]}")



