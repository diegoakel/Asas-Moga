import os
import re
import math
import inspect
import subprocess as sp

import numpy
import Modelo
import constantes

class asa():
    def __init__(self):
        self.viavel = constantes.solucao_inviavel
    
    def setar_secoes(self, envs, cordas, offsets):
        self.envs = envs
        self.offsets = offsets
        self.cordas = cordas
        self.setar_area(envs, cordas)

    def setar_area(self, envs, cordas):
        total = 0
        for i in range(0,len(envs)-1):
            if (i == 0):
                total += ((cordas[i] + cordas[i+1])*envs[i])/2
            else:
                total += ((cordas[i] + cordas[i+1])*(envs[i]-envs[i-1]))/2      
        
        self.wingspan = (self.envs[-1]*2)
        self.S = total*2
        self.AR = self.wingspan**2/self.S
        self.afil = self.cordas[-1]/self.cordas[0]
        self.mac = (self.cordas[0]*(2/3)* ((1+self.afil+self.afil**2)/(1+self.afil)))

    def escrever_macro(self): 
        escrever_macro(self)
        
    def executar_avl(self): 
        executar_avl(self)

    def coeficientes(self, limpar):
        coeficientes(self, limpar)

    def mtow (self):
        return  mtow(self)
           
    def calc_carga_paga (self):
        self.MTOW = self.calc_massa()[0]
        self.carga_paga = (self.MTOW - self.calc_massa()[1]) # Empirical
       
    def analisa(self, limpar):
        self.coeficientes(limpar)
        self.mtow()
        self.calc_carga_paga()

    def calc_massa(self):
        fator_corretivo = 1.09
        MTOW = ((self.W/Modelo.g)/fator_corretivo) # MTOW em kg
        self.massa_vazia = (1.539331*((self.S)**2)) + 1.341043*(self.S)
        return (MTOW, self.massa_vazia)

    def setar_secoes_intermediarias(self):
        self.coef_interpolation = Modelo.calcula_interpolador(self.envs, self.cordas)
        self.inter_corda, self.inter_offset, self.inter_envs, self.inter_num_p = Modelo.calcula_secoes(self.wingspan, self.coef_interpolation, self.envs, self.cordas, self.offsets)

        self.setar_area(self.inter_envs, self.inter_corda)

_asa = asa()
def executar_avl(self):
    commands  = open("comandos.avl" , "w")
    commands.write("load asa.avl\n"   +
    "oper\n" +
    "a\n" +
    "a %f\n" %(Modelo.alfa_stol) +
    "x\n" +
    "ft\n" +
    "resultado.txt\n" +
    "quit")
    commands.close()

    run_avl_command = 'avl.exe<' + 'comandos.avl'
    os.popen(run_avl_command).read()


def escrever_macro(self): # Não mexer nisso~
    file = f'''Urutau 2020 (2) 
    0.0                                 | Mach 
    0     0     0.0                     | iYsym  iZsym  Zsym
    {self.S}    {self.mac}     {self.wingspan}   | Sref   Cref   Bref 
    0.00000     0.00000     0.00000   | Xref   Yref   Zref
    0.00                               | CDp  (optional)
    SURFACE                      | (keyword)
    Main Wing
    {Modelo.num_elementos_corda}        1.0
    INDEX                        | (keyword)
    1814                         | Lsurf
    YDUPLICATE
    0.0
    SCALE
    1.0  1.0  1.0
    TRANSLATE
    0.0  0.0  0.0
    ANGLE
    0.000                         | dAinc'''

    for i in range(0, len(self.inter_envs)):
        section =     f'''\nSECTION                                              |  (keyword)
        {self.inter_offset[i]}    {self.inter_envs[i]}   0.0000    {self.inter_corda[i]}  0.000    {self.inter_num_p[i]}    3   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]
        AFIL 0.0 1.0
        airfoil.dat \n'''

        file = file + section

    o  = open("asa.avl", "w")
    o.write(file)
    o.close()


def limpar_arquivos():
    dirList = os.listdir()
    arquivo = ""
    for file in dirList:
        if (file == "asa.avl") or (file == "resultado.txt") or  (file == "comandos.txt"):
            arquivo = file
            os.remove(arquivo)

def coeficientes(self, limpar):
    self.setar_secoes_intermediarias()
    self.escrever_macro()
    self.executar_avl()

    results = (open("resultado.txt")).readlines()

    coefficients = []
    for line in results:
        matches = re.findall(r"\d\.\d\d\d\d", line)
        for value in matches:
            coefficients.append(float(value))

    self.CD  = coefficients[-7]
    self.CL = coefficients[-8]    
    self.e =  coefficients[-1]   

    if limpar:
        limpar_arquivos()
    

def mtow(self):    
    for k in range (0, 270):
        if (self.CL == 0) or (self.S < 0):
            Slo = 2*Modelo.comprimento_pista_maxima
            W = 0
        else:
            W = (k/(9)) * Modelo.g
            V = math.sqrt((2*W)/(Modelo.rho_ar*self.S*self.CL)) * 1.2 * 0.7
            T = Modelo.a*((V*0.7)**2)+Modelo.b*(V*0.7)+Modelo.c
            D = 0.5*Modelo.rho_ar*V**2*self.S*self.CD
            L = 0.5*Modelo.rho_ar*V**2*self.S*self.CL
            Slo = round((1.44*(W)**(2))/(Modelo.g*Modelo.rho_ar*self.S*self.CL*(T-(D+Modelo.mi_solo*(W-L)))), 2)
        
        if Slo > Modelo.comprimento_pista_maxima:
            break    

    self.W = W # MTOW em Newton
    return W

def calcula_carga_paga(real_env, real_corda, real_offset, limpar=True):
    _asa.setar_secoes(real_env, real_corda, real_offset)
    _asa.analisa(limpar)
    
    global parametros_temp
    parametros_temp = [_asa.S, _asa.CL, _asa.CD, _asa.massa_vazia]
    [parametros_temp.append(i) for i in _asa.coef_interpolation]
    [parametros_temp.append(i) for i in _asa.inter_corda]

    return _asa.carga_paga

def retorna_envergadura(real_env, real_corda, real_offset):
    return (2 * real_env[2])

def retorna_corda_1(real_env, real_corda, real_offset):
    return real_corda[1]

def retorna_corda_2(real_env, real_corda, real_offset):
    return real_corda[2]

def retorna_corda_ponta(real_env, real_corda, real_offset):
    return real_corda[3]

def retorna_menor_corda(real_env, real_corda, real_offset):
    _asa.setar_secoes(real_env, real_corda, real_offset)
    _asa.setar_secoes_intermediarias()

    return (min(_asa.inter_corda))

def retorna_delta_envergadura_2(real_env, real_corda, real_offset):
    return (real_env[1]- real_env[0])

def retorna_delta_envergadura_3(real_env, real_corda, real_offset):
    return (real_env[2]- real_env[1])

def delta_corda_1(real_env, real_corda, real_offset):
    return (real_corda[1]-real_corda[0])

def delta_corda_2(real_env, real_corda, real_offset):
    return (real_corda[2]-real_corda[1])

def delta_corda_3(real_env, real_corda, real_offset):
    return (real_corda[3]-real_corda[2])

def delta_offset2(real_env, real_corda, real_offset):
    return (real_offset[1]-real_offset[0])

def delta_offset3(real_env, real_corda, real_offset):
    return (real_offset[2]-real_offset[1])

def retorna_parametros():
    return parametros_temp