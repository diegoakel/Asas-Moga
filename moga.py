import random as rd
import pandas as pd
from Asa import asa

def crossover(l, q): 
    l,q = int(str(l)[2:8]), int(str(q)[2:8]) # Corta a parte decimal
    # 
    # Ve se tem menos de 6 digitos e ajeita
    # Verificar isso
    while (len(str(l))< 6):
        l = l*10
    while (len(str(q))< 6):
        q = q*10

    l,q = bin(l)[2:], bin(q)[2:] # Corta o "0b"
    #l,q = str(l).zfill(22), str(q).zfill(22) # Deixa no mesmo tamanho

    l = list(l) 
    q = list(q) 

    ponto_corte = rd.randint(5, 17) # (0,n)
    # Combinando a partir do ponto de corte
    l[ponto_corte:], q[ponto_corte:] = q[ponto_corte:], l[ponto_corte:] 

    # Volta pra string
    filho_1 = ''.join(l) 

    filho_1 = int(filho_1, 2)/1000000

    return filho_1

def genetico(asas_populacao, modo = 'classic', dados = 'DataFrame', analisar = (True, "MTOW")):
    populacao = sorted(asas_populacao, key = lambda x: x.pontuacao, reverse=True)
    # melhores = []
    '''
    for i in populacao:
        i.analisador()
    populacao = sorted(populacao, key = lambda x: x.pontuacao, reverse=True)
    '''
    limite_populacional = len(populacao)
    # cruzamentos
    ciclos = (int(round(limite_populacional/2)))
    tamanho = len(populacao) - 1
    
    # gerações
    for i in range (0, limite_populacional): # Combina todos os indivíduos n=limite_populacional vezes
        for j in range (0, ciclos):
            filho1 = mod_comb(populacao[j], populacao[tamanho-j], modo = 'classic')
            #filho2 = combinador(populacao[tamanho-i], populacao[i])
            filho1.analisa()
            populacao.append(filho1)
            #populacao.append(filho2)
            
        populacao = sorted(populacao, key=lambda x: x.pontuacao, reverse=True)
    
        # Deletar os extras acima do limite populacional
        if len(populacao) > limite_populacional:
            for i in range (limite_populacional, len(populacao)-1):
                del populacao[limite_populacional]
                      
    if(dados == 'DataFrame'):
        DataFrame = pd.DataFrame()
        for i, j in zip(populacao, range(0, len(populacao))):
            data = [[i.S, i.B, i.AR, i.afil]]
            asa = pd.DataFrame(data, columns=['AREA','ENVERGADURA', 'AR' , 'AFILAMENTO'], index = [j])
            DataFrame = DataFrame.append(asa)
         
        return populacao
        
def mod_comb(asa1, asa2, modo = 'classic'):
    # Cruzar o genoma
    '''
    Forma como as duas asas pais são combinadas.
    '''
    if(modo == 'classic'):
        cordas = []
        for i in range (0,len(asa1.cordas)):
            corda = crossover(asa1.cordas[i],asa2.cordas[i])
            cordas.append(corda)
        cordas = sorted(cordas)

        # # Reduzir pro limite de 0,37
        # if (cordas[0] > 0.37):
        #     while (cordas[0] > 0.37):
        #         cordas[0] = cordas[0]*0.991
        #         cordas = sorted(cordas)

        # # Ajeitar o afilamento
        # if (cordas[-1]/cordas[0] >= 0.4):
        #     while (cordas[-1]/cordas[0] >= 0.4):
        #         cordas[-1] = cordas[-1]*0.991
        # else:
        #     while (cordas[-1]/cordas[0] < 0.3):
        #         cordas[-1] = cordas[-1]*1.05
        # cordas = sorted(cordas)   

        # Envergaduras
        envs = []
        for i in range (0, len(asa1.envs)):
            if (i == 0):
                env = crossover(asa1.envs[i],asa2.envs[i])
            else:
                env = crossover(asa1.envs[i] - asa1.envs[i-1], asa2.envs[i] - asa2.envs[i-1])
            envs.append(env)
        
        for i in range(0, len(envs)):
            if (i != 0):
                envs[i] = envs[i] + envs[i-1]

        # PReparar
        # Add esse limite de envergadura
        # if (env[-1]>= limite_envergadura):

        # Combinar
        # Offset calculations: Botar só uma mutação
        offsets = asa1.offsets
        filho = asa(envs, cordas, offsets)
        return filho

