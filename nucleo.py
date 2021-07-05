# Esse é o repositório aboluto.

from interface import Otimizacao_Iniciada
import Moga_2020
import time
import interface
import Modelo
import analise 

for j in range(0,1): # Grau
    Modelo.grau_interpolacao = j
    for i in range(1,2): # Execuções
        path = f"../Resultados/grau={Modelo.grau_interpolacao}/"
        label = f"Journal_aero_{Modelo.grau_interpolacao}_{Modelo.pop_size}_{Modelo.max_gen}_R{i}"
        nome_otimizacao = path+label

        interface.Otimizacao_Iniciada(nome_otimizacao)

        inicio = time.time()
        pop_new = []
        # analise.calcula_carga_paga([0.64, 1.33, 2.04],[0.4, 0.28, 0.27, 0.07],[0,0,0], False)

        Moga_2020.Evolucao(pop_new)
        fim = time.time()
        total = fim-inicio

        interface.Otimizacao_Finalizada(path, label, total, Moga_2020.cont_analise_historico[0], Moga_2020.cont_analise_nova[0], Moga_2020.cont_analise_pre_check[0])
