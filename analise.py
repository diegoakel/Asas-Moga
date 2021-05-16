import os
import re
import math
import Asa

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

def coeficientes(self, angulo):
    
    self.file_and_commands(angulo)

    run_avl_command = 'avl.exe<' + 'comandos.avl'
    os.popen(run_avl_command).read()


    results = (open("resultado.txt")).readlines()
    coefficients = []
    for line in results:
        matches = re.findall(r"\d\.\d\d\d\d", line)
        for value in matches:
            coefficients.append(float(value))
    

    CD = coefficients[-7]
    CL = coefficients[-8]    
    e =  coefficients[-1]     

    self.CD = CD
    self.CL = CL
    self.e = e
    
    # Limpar
    dirList = os.listdir()
    arquivo = ""
    for file in dirList:
        if (file == "asa.avl") or (file == "resultado.txt") or  (file == "comandos.txt"):
            arquivo = file
            os.remove(arquivo)
    
    #return (CD_CL)

def mtow(self, rho, coeficientes):
    a = coeficientes[0]
    b = coeficientes[1]
    c = coeficientes[2]
    
    for k in range (0, 270):
        W= (k/(9)) * self.g
        V = math.sqrt((2*W)/(self.rho*self.S*self.CL)) * 1.2 * 0.7
        T = a*((V*0.7)**2)+b*(V*0.7)+c
        D = self.drag(V) #self.rho*V**(2)*0.5*self.CD*self.S
        L = self.lift(V) #self.rho*V**(2)*0.5*self.CL*self.S
        Slo = round((1.44*(W)**(2))/(self.g*self.rho*self.S*self.CL*(T-(D+self.mi*(W-L)))), 2)
        
        if Slo > self.pista_total:
            break    

    self.W = W # MTOW em Newton
    return W


def analisa(self, metodo_massa):
    '''
    Retorna uma lista com alguns resultados de analise da asa.
    
    metodo_massa: metodo com qual se estima a massa da asa
    
        'MTOW' = Estima a massa com base no MTOW de acordo com dados passados 
        
        'RAZAO' = Estima a massa com base na razao entre o peso de asas anteriores projetadas e suas areas
                    logo o parametro a ser dados para esse metodo é a area da asa que deseja estimar sua massa
    '''
    # Calculos para situação de stol
    self.coeficientes(self.alfa_stol)
    self.mtow()
    self.calc_pontuacao(metodo_massa)

    # Calculos para a polar
    self.CD_lista = []
    self.CL_lista = []
    self.e_lista = []
    self.alfa_lista = []

    for i in range(12, 15, 1):
        self.coeficientes(i)
        self.CD_lista.append(self.CD)
        self.CL_lista.append(self.CL)
        self.e_lista.append(self.e)
        self.alfa_lista.append(i)

    data = [self.S, self.B, self.AR,  self.afil, self.MTOW, self.carga_paga,
        self.pontuacao, self.alfa_lista, self.CD_lista, self.CL_lista]

    return data


def fake_analisa(x):
    fake_env = [x[0],x[0]+ x[1],x[0] + x[1] + x[2]]
    fake_corda = [x[3],x[3] - x[4], x[3] - x[4] - x[5], x[3]- x[4] - x[5] - x[6]]
    fake_offset = [x[7], x[7] + x[8], x[7] + x[8] + x[9]]


    _asa = Asa.asa(fake_env,fake_corda, fake_offset)
    _asa.analisa()

    return _asa.pontuacao



def metodo_por_MTOW(MTOW , PORCENTAGEM = 15):
    '''
    Geralmente a massa da asa é 30 porcento da carga vazia
    Geralmente a massa da asa é 9 porcento do MTOW (NEWTON POR NEWTON)
    '''
    # G = 9.81 #m/s^2
    
    m = MTOW * (PORCENTAGEM / 100)
    return m


def metodo_por_constante(AREA_OBJETIVO, PESO = 0, AREA = 0, CONSTANTE = 20.3605):
    '''
    Geralmente a constante PESO DA ASA / AREA DA ASA É 15,8
    '''
    G = 9.81 #m/s^2
        
    if CONSTANTE != 0:

        PESO_OBJETIVO = CONSTANTE * AREA_OBJETIVO

        m = PESO_OBJETIVO / G
    
    else:
        
        CONSTANTE = PESO / AREA

        PESO_OBJETIVO = CONSTANTE * AREA_OBJETIVO

        m = PESO_OBJETIVO / G


    return m

def calc_massa(self, metodo_massa):

    fator_corretivo = 1.09
    MTOW = ((self.W/self.g)/fator_corretivo) # MTOW em kg
    
    massa_vazia = (11.48*((self.S)**2)) - 26.55*(self.S) + 19.44
    
    if(metodo_massa == 'MTOW'):
        self.massa_asa = metodo_por_MTOW(MTOW)
        
    elif(metodo_massa == 'RAZAO'):
        self.massa_asa = metodo_por_constante(self.S)
        
    massa_resto = massa_vazia - self.massa_asa 
    
    return (MTOW, massa_vazia, self.massa_asa, massa_resto)