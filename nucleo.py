# Esse é o repositório aboluto.

from interface import Otimizacao_Iniciada
import Moga_2020
import time
import interface
import Modelo
import analise

interface.Otimizacao_Iniciada(Modelo.nome_otimizacao)

inicio = time.time()
pop_new = []
# analise.calcula_carga_paga([0.64, 1.33, 2.04],[0.4, 0.28, 0.27, 0.07],[0,0,0], False)
Moga_2020.Evolucao(pop_new)
fim = time.time()
total = fim-inicio

interface.Otimizacao_Finalizada(Modelo.nome_otimizacao, total, Moga_2020.cont_analise_historico[0], Moga_2020.cont_analise_nova[0], Moga_2020.cont_analise_pre_check[0])