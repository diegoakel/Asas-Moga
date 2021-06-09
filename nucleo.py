# Esse é o repositório aboluto.

from interface import Otimizacao_Iniciada
import Moga_2020
import time
import interface
import Modelo

interface.Otimizacao_Iniciada(Modelo.nome_otimizacao)

inicio = time.time()
pop_new = []
Moga_2020.Evolucao(pop_new)
fim = time.time()
total = fim-inicio

interface.Otimizacao_Finalizada(Modelo.nome_otimizacao, total, Moga_2020.cont_analise_historico[0], Moga_2020.cont_analise_nova[0], Moga_2020.cont_analise_pre_check[0])