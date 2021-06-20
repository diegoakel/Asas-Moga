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
    
    def setar_geometria(self, B, cordas, offsets):
        self.envs = B
        self.wingspan = (B[-1]*2)
        self.offsets = offsets
        self.cordas = cordas
        self.S = (self.calcula_area(B, cordas)*2)
        self.AR = self.wingspan**2/self.S
        self.afil = cordas[-1]/cordas[0]
        self.mac = ( cordas[0]*(2/3)* ((1+self.afil+self.afil**2)/(1+self.afil)))

    def calcula_area(self, vetor_env, vetor_corda):
        total = 0
        for i in range(0,len(vetor_env)-1):
            if (i == 0):
                total += ((vetor_corda[i] + vetor_corda[i+1])*vetor_env[i])/2
            else:
                total += ((vetor_corda[i] + vetor_corda[i+1])*(vetor_env[i]-vetor_env[i-1]))/2      

        return total  


    def file_and_commands(self): # Não mexer nisso~
        file_and_commands(self)
        
    def coeficientes(self):
        coeficientes(self)
    
    def lift (self, V):
        return (Modelo.rho_ar*V**(2)*0.5*self.CL*self.S)
    
    def drag (self, V):
        return (Modelo.rho_ar*V**(2)*0.5*self.CD*self.S)

    def mtow (self):
        return  mtow(self)
           
    def calc_pontuacao (self):
        self.MTOW = self.calc_massa()[0]
        self.carga_paga = (self.MTOW - self.calc_massa()[1]) # Empirical
        self.pontuacao = self.carga_paga
       
    def analisa(self):
        # Calculos para situação de stol
        self.coeficientes()
        self.mtow()
        self.calc_pontuacao()

        data = [self.S, self.wingspan, self.AR,  self.afil, self.MTOW, self.carga_paga,
            self.pontuacao, self.alfa_lista, self.CD_lista, self.CL_lista]

        return data

    def calc_massa(self):
        fator_corretivo = 1.09
        MTOW = ((self.W/Modelo.g)/fator_corretivo) # MTOW em kg
        self.massa_vazia = (1.539331*((self.S)**2)) + 1.341043*(self.S)
        return (MTOW, self.massa_vazia)


_asa = asa()

def file_and_commands(self): # Não mexer nisso~
    num_p1 =  math.ceil(self.envs[0]/Modelo.comprimento_elemento_env) -1
    num_p2 =  math.ceil((self.envs[1]-self.envs[0])/Modelo.comprimento_elemento_env) -1
    num_p3 =  math.ceil((self.envs[2]-self.envs[1])/Modelo.comprimento_elemento_env) -1
    num_sections = 11

    self.coef_interpolation = Modelo.calcula_secoes(self.envs, self.cordas)

    vetor_corda = []
    vetor_envs = []
    for i in range (0, num_sections):
        vetor_envs.append(i*self.wingspan/(2*(num_sections-1)))
        vetor_corda.append(Modelo.calcula_corda(vetor_envs[i], self.coef_interpolation))
    
    area = self.calcula_area(vetor_envs, vetor_corda)

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

    for i in range(0, num_sections):


        section =     f'''\nSECTION                                              |  (keyword)
        0.0000    {vetor_envs[i]}   0.0000    {vetor_corda[i]}  0.000    {num_p1}    3   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]
        AFIL 0.0 1.0
        airfoil.dat'''

        file = file + section

    # "SECTION                                              |  (keyword)\n"+
    # f"0.0000    0.0000    0.0000    %f   0.000    {num_p1}    3   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n" %(self.cordas[0])+
    # "AFIL 0.0 1.0\n"+
    # "airfoil.dat\n"+
    # "SECTION                                                     |  (keyword)\n" +
    # f"%f    %f    0.0000    %f   0.000    {num_p2}    3   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n" %( self.offsets[0],  self.envs[0], self.cordas[1])+
    # "AFIL 0.0 1.0\n"+
    # "airfoil.dat\n"+
    # "SECTION                                                     |  (keyword)\n" +
    # f"%f   %f    0.0000    %f   0.000   {num_p3}    3   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n" %( self.offsets[1],  self.envs[1], self.cordas[2])+
    # "AFIL 0.0 1.0\n"+
    # "airfoil.dat \n" +
    # "SECTION                                                     |  (keyword)\n" +
    # "%f    %f    0.0000    %f   0.000   13    3   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n" %( self.offsets[2],  self.envs[2], self.cordas[3])+
    # "AFIL 0.0 1.0\n" +
    # "airfoil.dat \n"


    o  = open("asa.avl", "w")
    o.write(file)
    o.close()

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


def coeficientes(self):
    
    self.file_and_commands()

    run_avl_command = 'avl.exe<' + 'comandos.avl'
    os.popen(run_avl_command).read()

    results = (open("resultado.txt")).readlines()
    coefficients = []
    for line in results:
        matches = re.findall(r"\d\.\d\d\d\d", line)
        for value in matches:
            coefficients.append(float(value))

    self.CD  = coefficients[-7]
    self.CL = coefficients[-8]    
    self.e =  coefficients[-1]     
    
    # Limpar
    dirList = os.listdir()
    arquivo = ""
    for file in dirList:
        if (file == "asa.avl") or (file == "resultado.txt") or  (file == "comandos.txt"):
            arquivo = file
            os.remove(arquivo)

def mtow(self):    
    for k in range (0, 270):
        if (self.CL == 0) or (self.S < 0):
            Slo = 2*Modelo.comprimento_pista_maxima
            W = 0
        else:
            W = (k/(9)) * Modelo.g
            V = math.sqrt((2*W)/(Modelo.rho_ar*self.S*self.CL)) * 1.2 * 0.7
            T = Modelo.a*((V*0.7)**2)+Modelo.b*(V*0.7)+Modelo.c
            D = self.drag(V) 
            L = self.lift(V)
            Slo = round((1.44*(W)**(2))/(Modelo.g*Modelo.rho_ar*self.S*self.CL*(T-(D+Modelo.mi_solo*(W-L)))), 2)
        
        if Slo > Modelo.comprimento_pista_maxima:
            break    

    self.W = W # MTOW em Newton
    return W

def calcula_carga_paga(real_env, real_corda, real_offset):
    _asa.setar_geometria(real_env, real_corda, real_offset)
    _asa.analisa()
    # _asa.salva_asa(gen_no,n)
    
    global parametros_temp
    parametros_temp = []
    parametros_temp.append(_asa.S)
    parametros_temp.append(_asa.CL)
    parametros_temp.append(_asa.CD)
    parametros_temp.append(_asa.massa_vazia)
    print (_asa.coef_interpolation)
    [parametros_temp.append(i) for i in _asa.coef_interpolation]

    return _asa.pontuacao


def retorna_envergadura(real_env, real_corda, real_offset):
    return (2 * real_env[2])

def retorna_corda_1(real_env, real_corda, real_offset):
    return real_corda[1]

def retorna_corda_2(real_env, real_corda, real_offset):
    return real_corda[2]

def retorna_corda_ponta(real_env, real_corda, real_offset):
    return real_corda[3]

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