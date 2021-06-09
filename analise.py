import os
import re
import math
import inspect
import subprocess as sp
import Modelo
import constantes
class asa():
    def __init__(self):
        self.viavel = constantes.solucao_inviavel
    
    def setar_geometria(self, B, cordas, offsets, alfa_stol = 13.5):
        self.envs = B
        self.B = (B[-1]*2)
        self.offsets = offsets
        self.cordas = cordas

        total = 0
        for i in range(0,len(B)):
            if (i == 0):
                total += ((cordas[i] + cordas[i+1])*B[i])/2
            else:
                total += ((cordas[i] + cordas[i+1])*(B[i]-B[i-1]))/2

        self.S = (total*2)
        self.AR = self.B**2/self.S
        self.afil = cordas[-1]/cordas[0]
        self.mac = ( cordas[0]*(2/3)* ((1+self.afil+self.afil**2)/(1+self.afil)))
        self.alfa_stol = alfa_stol

        # Valores que não são da aeronave
        self.g = Modelo.g
        self.rho = Modelo.rho_ar
        self.mi = Modelo.mi_solo
        self.pista_total = Modelo.comprimento_pista_maxima

    def file_and_commands(self, alfa_stol = 13.5): # Não mexer nisso~
        file_and_commands(self,alfa_stol)
        
    def coeficientes(self, angulo):
        coeficientes(self, angulo)
    
    def lift (self, V, rho = 1.225 ):
        return (self.rho*V**(2)*0.5*self.CL*self.S)
    
    def drag (self, V, rho = 1.225 ):
        return (self.rho*V**(2)*0.5*self.CD*self.S)

    def mtow (self, rho = 1.225, coeficientes = (-0.0126, -0.5248, 40.0248)):
        return  mtow(self, rho, coeficientes)
           
    def calc_pontuacao (self):
        self.MTOW = self.calc_massa()[0]
        self.carga_paga = (self.MTOW - self.calc_massa()[1]) # Empirical
        self.pontuacao = self.carga_paga
       
    def analisa(self):
        # Calculos para situação de stol
        self.coeficientes(self.alfa_stol)
        self.mtow()
        self.calc_pontuacao()

        # Calculos para a polar
        self.CD_lista = []
        self.CL_lista = []
        self.e_lista = []
        self.alfa_lista = []

        # for i in range(13, 14, 1):
        #     self.coeficientes(i)
        #     self.CD_lista.append(self.CD)
        #     self.CL_lista.append(self.CL)
        #     self.e_lista.append(self.e)
        #     self.alfa_lista.append(i)

        data = [self.S, self.B, self.AR,  self.afil, self.MTOW, self.carga_paga,
            self.pontuacao, self.alfa_lista, self.CD_lista, self.CL_lista]

        return data

    def calc_massa(self):
        fator_corretivo = 1.09
        MTOW = ((self.W/self.g)/fator_corretivo) # MTOW em kg
        self.massa_vazia = (1.539331*((self.S)**2)) + 1.341043*(self.S)
        return (MTOW, self.massa_vazia)

    def salva_asa(self, geracao,n):
        o  = open(f"../Banco_asas/asas_todas10/geracao_{geracao}_individuo{n}.avl", "w")
        o.write(" Urutau 2020 (2)\n" +
        "0.0                                 | Mach\n" +
        "0     0     0.0                     | iYsym  iZsym  Zsym\n"+
        "%f     %f     %f   | Sref   Cref   Bref\n" %(self.S, self.mac, self.B)+
        "0.00000     0.00000     0.00000   | Xref   Yref   Zref\n"+
        "0.00                               | CDp  (optional)\n"+
        "SURFACE                      | (keyword)\n"+
        "Main Wing\n"+
        "11        1.0\n"+
        "INDEX                        | (keyword)\n"+
        "1814                         | Lsurf\n"+
        "YDUPLICATE\n"+
        "0.0\n"+
        "SCALE\n"+
        "1.0  1.0  1.0\n"+
        "TRANSLATE\n"+
        "0.0  0.0  0.0\n"+
        "ANGLE\n"+
        "0.000                         | dAinc\n"+
        "SECTION                                              |  (keyword)\n"+
        "0.0000    0.0000    0.0000    %f   0.000    8    3   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n" %(self.cordas[0])+
        "AFIL 0.0 1.0\n"+
        "airfoil.dat\n"+
        "SECTION                                                     |  (keyword)\n" +
        "%f    %f    0.0000    %f   0.000    8    3   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n" %( self.offsets[0],  self.envs[0], self.cordas[1])+
        "AFIL 0.0 1.0\n"+
        "airfoil.dat\n"+
        "SECTION                                                     |  (keyword)\n" +
        "%f   %f    0.0000    %f   0.000   13    1   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n" %( self.offsets[1],  self.envs[1], self.cordas[2])+
        "AFIL 0.0 1.0\n"+
        "airfoil.dat \n" +
        "SECTION                                                     |  (keyword)\n" +
        "%f    %f    0.0000    %f   0.000   13    1   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n" %( self.offsets[2],  self.envs[2], self.cordas[3])+
        "AFIL 0.0 1.0\n" +
        "airfoil.dat \n" +
        f"#{self.pontuacao} \n" +
        f"#{self.CL}00000 \n" +
        f"#{self.CD}00000 \n" +
        f"#{self.massa_vazia} \n" +
        f'#{self.viavel}'
        # 
        )
        o.close()

_asa = asa()

def file_and_commands(self, alfa_stol): # Não mexer nisso~

    o  = open("asa.avl", "w")
    o.write(" Urutau 2020 (2)\n" +
    "0.0                                 | Mach\n" +
    "0     0     0.0                     | iYsym  iZsym  Zsym\n"+
    "%f     %f     %f   | Sref   Cref   Bref\n" %(self.S, self.mac, self.B)+
    "0.00000     0.00000     0.00000   | Xref   Yref   Zref\n"+
    "0.00                               | CDp  (optional)\n"+
    "SURFACE                      | (keyword)\n"+
    "Main Wing\n"+
    "11        1.0\n"+
    "INDEX                        | (keyword)\n"+
    "1814                         | Lsurf\n"+
    "YDUPLICATE\n"+
    "0.0\n"+
    "SCALE\n"+
    "1.0  1.0  1.0\n"+
    "TRANSLATE\n"+
    "0.0  0.0  0.0\n"+
    "ANGLE\n"+
    "0.000                         | dAinc\n"+
    "SECTION                                              |  (keyword)\n"+
    "0.0000    0.0000    0.0000    %f   0.000    8    3   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n" %(self.cordas[0])+
    "AFIL 0.0 1.0\n"+
    "airfoil.dat\n"+
    "SECTION                                                     |  (keyword)\n" +
    "%f    %f    0.0000    %f   0.000    8    3   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n" %( self.offsets[0],  self.envs[0], self.cordas[1])+
    "AFIL 0.0 1.0\n"+
    "airfoil.dat\n"+
    "SECTION                                                     |  (keyword)\n" +
    "%f   %f    0.0000    %f   0.000   13    1   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n" %( self.offsets[1],  self.envs[1], self.cordas[2])+
    "AFIL 0.0 1.0\n"+
    "airfoil.dat \n" +
    "SECTION                                                     |  (keyword)\n" +
    "%f    %f    0.0000    %f   0.000   13    1   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n" %( self.offsets[2],  self.envs[2], self.cordas[3])+
    "AFIL 0.0 1.0\n" +
    "airfoil.dat \n")
    o.close()

    commands  = open("comandos.avl" , "w")
    commands.write("load asa.avl\n"   +
    "oper\n" +
    "a\n" +
    "a %f\n" %(alfa_stol) +
    "x\n" +
    "ft\n" +
    "resultado.txt\n" +
    "quit")
    commands.close()

# def Popen(*args, **kwargs):
#     sig = inspect.signature(real_popen)
#     bound_args = sig.bind(*args, **kwargs).arguments
#     bound_args['stdout'] = subprocess.DEVNULL
#     bound_args['stderr'] = subprocess.DEVNULL
#     return real_popen(**bound_args)

# real_popen = subprocess.Popen
# subprocess.Popen = Popen

def coeficientes(self, angulo):
    
    self.file_and_commands(angulo)

    run_avl_command = 'avl.exe<' + 'comandos.avl'
    os.popen(run_avl_command).read()

    # avl = sp.Popen(['avl.exe'],
    #     stdin=sp.PIPE,stdout=None, 
    #     stderr=None, 
    #     universal_newlines=True)
    # avl.stdin.write("comandos.avl" +'\n')
    # avl.communicate('comandos.avl')
    # sp.Popen(['avl.exe', "comandos.avl"])


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

def mtow(self, rho, coeficientes):
    a = coeficientes[0]
    b = coeficientes[1]
    c = coeficientes[2]
    
    for k in range (0, 270):
        if (self.CL == 0) or (self.S < 0):
            Slo = 2*self.pista_total
            W = 0
        else:
            W = (k/(9)) * self.g
            V = math.sqrt((2*W)/(self.rho*self.S*self.CL)) * 1.2 * 0.7
            T = a*((V*0.7)**2)+b*(V*0.7)+c
            D = self.drag(V) #self.rho*V**(2)*0.5*self.CD*self.S
            L = self.lift(V) #self.rho*V**(2)*0.5*self.CL*self.S
            Slo = round((1.44*(W)**(2))/(self.g*self.rho*self.S*self.CL*(T-(D+self.mi*(W-L)))), 2)
        
        if Slo > self.pista_total:
            break    

    self.W = W # MTOW em Newton
    return W

def calcula_carga_paga(x,gen_no,n):
    fake_env = [x[0],x[1],x[2]]
    fake_corda = [x[3],x[4],x[5],x[6]]
    fake_offset = [x[7], x[8], x[9]]

    _asa.setar_geometria(fake_env,fake_corda, fake_offset)
    _asa.analisa()
    _asa.salva_asa(gen_no,n)
    
    return _asa.pontuacao

def seta_viabilidade(viavel):
    _asa.viavel = viavel

def retorna_envergadura(x):
    fake_env = [x[0],x[1],x[2]]
    return (2*fake_env[2])

def retorna_corda_1(x):
    fake_corda = [x[3],x[4],x[5],x[6]]
    return fake_corda[1]

def retorna_corda_2(x):
    fake_corda = [x[3],x[4],x[5],x[6]]
    return fake_corda[2]

def retorna_corda_ponta(x):
    fake_corda = [x[3],x[4],x[5],x[6]]
    return fake_corda[3]

def retorna_delta_envergadura_2(x):
    fake_env = [x[0],x[1],x[2]]
    return (fake_env[1]- fake_env[0])

def retorna_delta_envergadura_3(x):
    fake_env = [x[0],x[1],x[2]]
    return (fake_env[2]- fake_env[1])

def delta_corda_1(x):
    fake_corda = [x[3],x[4],x[5],x[6]]
    return (fake_corda[1]-fake_corda[0])

def delta_corda_2(x):
    fake_corda = [x[3],x[4],x[5],x[6]]
    return (fake_corda[2]-fake_corda[1])

def delta_corda_3(x):
    fake_corda = [x[3],x[4],x[5],x[6]]
    return (fake_corda[3]-fake_corda[2])

def delta_offset2(x):
    fake_offset = [x[7],x[8],x[9]]
    return (fake_offset[1]-fake_offset[0])

def delta_offset3(x):
    fake_offset = [x[7],x[8],x[9]]
    return (fake_offset[2]-fake_offset[1])
