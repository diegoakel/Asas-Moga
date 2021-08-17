from interface import Otimizacao_Iniciada
import Moga_2020
import time
import interface
import Modelo

for j in range(4, 5):  # Tipo de problema
    Modelo.tipo_problema = j

    if j == 4:
        Modelo.num_objetivos = 2

    for i in range(1, 2):  # Execuções
        path = f"Resultados/tipo={Modelo.tipo_problema}/"
        # path = f"Resultados/manuais/"

        label = (
            f"Journal_aero_{Modelo.tipo_problema}_{Modelo.pop_size}_{Modelo.max_gen}_R{i}"
        )
        nome_otimizacao = path + label

        interface.Otimizacao_Iniciada(nome_otimizacao)

        inicio = time.time()
        pop_new = []
        # analise.calcula_carga_paga([0.64, 1.33, 2.04],[0.4, 0.28, 0.27, 0.07],[0,0,0], False)

        Moga_2020.Evolucao(pop_new)
        fim = time.time()
        total = fim - inicio

        interface.Otimizacao_Finalizada(
            path,
            label,
            total,
            Moga_2020.cont_analise_historico[0],
            Moga_2020.cont_analise_nova[0],
            Moga_2020.cont_analise_pre_check[0],
        )
