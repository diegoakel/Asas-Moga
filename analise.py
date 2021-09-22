import os
import re
import math
import inspect
import subprocess as sp
import Modelo
import constantes
from dataclasses import dataclass, field

class Asa:
    def __init__(self):
        self.viavel = constantes.solucao_inviavel

    def setar_geometria(self, B, cordas, offsets, alfa_stol=13.5):
        self.envs = B
        self.wingspan = B[-1] * 2
        self.offsets = offsets
        self.cordas = cordas

        total = 0
        for i in range(0, len(B)):
            if i == 0:
                total += ((cordas[i] + cordas[i + 1]) * B[i]) / 2
            else:
                total += ((cordas[i] + cordas[i + 1]) * (B[i] - B[i - 1])) / 2

        self.S = total * 2
        self.AR = self.wingspan ** 2 / self.S
        self.afil = cordas[-1] / cordas[0]
        self.mac = (
            cordas[0] * (2 / 3) * ((1 + self.afil + self.afil ** 2) / (1 + self.afil))
        )

        # Valores que não são da aeronave
        self.g = Modelo.g
        self.rho = Modelo.rho_ar
        self.mi = Modelo.mi_solo
        self.pista_total = Modelo.comprimento_pista_maxima

    # def file_and_commands(self, alfa_stol=13.5):
    #     num_p1 = math.ceil(self.envs[0] / Modelo.comprimento_elemento_env) - 1
    #     num_p2 = (
    #         math.ceil((self.envs[1] - self.envs[0]) / Modelo.comprimento_elemento_env) - 1
    #     )
    #     num_p3 = (
    #         math.ceil((self.envs[2] - self.envs[1]) / Modelo.comprimento_elemento_env) - 1
    #     )

    #     o = open("asa.avl", "w")
    #     o.write(
    #         " Urutau 2020 (2)\n"
    #         + "0.0                                 | Mach\n"
    #         + "0     0     0.0                     | iYsym  iZsym  Zsym\n"
    #         + "%f     %f     %f   | Sref   Cref   Bref\n"
    #         % (self.S, self.mac, self.wingspan)
    #         + "0.00000     0.00000     0.00000   | Xref   Yref   Zref\n"
    #         + "0.00                               | CDp  (optional)\n"
    #         + "SURFACE                      | (keyword)\n"
    #         + "Main Wing\n"
    #         + f"{Modelo.num_elementos_corda}        1.0\n"
    #         + "INDEX                        | (keyword)\n"
    #         + "1814                         | Lsurf\n"
    #         + "YDUPLICATE\n"
    #         + "0.0\n"
    #         + "SCALE\n"
    #         + "1.0  1.0  1.0\n"
    #         + "TRANSLATE\n"
    #         + "0.0  0.0  0.0\n"
    #         + "ANGLE\n"
    #         + "0.000                         | dAinc\n"
    #         + "SECTION                                              |  (keyword)\n"
    #         + f"0.0000    0.0000    0.0000    %f   0.000    {num_p1}    3   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n"
    #         % (self.cordas[0])
    #         + "AFIL 0.0 1.0\n"
    #         + "airfoil.dat\n"
    #         + "SECTION                                                     |  (keyword)\n"
    #         + f"%f    %f    0.0000    %f   0.000    {num_p2}    3   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n"
    #         % (self.offsets[0], self.envs[0], self.cordas[1])
    #         + "AFIL 0.0 1.0\n"
    #         + "airfoil.dat\n"
    #         + "SECTION                                                     |  (keyword)\n"
    #         + f"%f   %f    0.0000    %f   0.000   {num_p3}    3   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n"
    #         % (self.offsets[1], self.envs[1], self.cordas[2])
    #         + "AFIL 0.0 1.0\n"
    #         + "airfoil.dat \n"
    #         + "SECTION                                                     |  (keyword)\n"
    #         + "%f    %f    0.0000    %f   0.000   13    3   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n"
    #         % (self.offsets[2], self.envs[2], self.cordas[3])
    #         + "AFIL 0.0 1.0\n"
    #         + "airfoil.dat \n"
    #     )
    #     o.close()

    #     commands = open("comandos.avl", "w")
    #     commands.write(
    #         "load asa.avl\n"
    #         + "oper\n"
    #         + "a\n"
    #         + "a %f\n" % (alfa_stol)
    #         + "x\n"
    #         + "ft\n"
    #         + "resultado.txt\n"
    #         + "quit"
    #     )
    #     commands.close()

    def escrever_macro(self):
        file = f"""Urutau 2020 (2) 
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
        0.000                         | dAinc"""

        for i in range(0, len(self.inter_envs)):
            section = f"""\nSECTION                                              |  (keyword)
            {self.inter_offset[i]}    {self.inter_envs[i]}   0.0000    {self.inter_corda[i]}  0.000    {self.inter_num_p[i]}    3   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]
            AFIL 0.0 1.0
            airfoil.dat \n"""

            file = file + section

        o = open("asa.avl", "w")
        o.write(file)
        o.close()

    def executar_avl(self):
        """
        Abre e executa os comandos no AVL.
        """        
        commands = open("comandos.avl", "w")
        commands.write(
            "load asa.avl\n"
            + "oper\n"
            + "a\n"
            + "a %f\n" % (Modelo.alfa_stol)
            + "x\n"
            + "ft\n"
            + "resultado.txt\n"
            + "quit"
        )
        commands.close()

        run_avl_command = "avl.exe<" + "comandos.avl"
        os.popen(run_avl_command).read()

    def coeficientes(self, limpar):
        """
        Calcula os coeficientes aerodinâmicos

        :param limpar: Se deseja limpar os arquivos'
        :type limpar: Boolean
        """
        self.inter_corda = self.cordas
        self.inter_envs = [0]
        self.inter_offset = [0]
        self.inter_num_p = [11, 11, 11, 11]
        [self.inter_envs.append(item) for item in self.envs]
        [self.inter_offset.append(item) for item in self.offsets]
        self.escrever_macro()
        self.executar_avl()

        results = (open("resultado.txt")).readlines()

        coefficients = []
        for line in results:
            matches = re.findall(r"\d\.\d\d\d\d", line)
            for value in matches:
                coefficients.append(float(value))

        self.CD = coefficients[-7]
        self.CL = coefficients[-8]
        self.e = coefficients[-1]

        if limpar:
            limpar_arquivos()

    def mtow(self):
        for k in range(0, 270):
            if (self.CL == 0) or (self.S < 0):
                Slo = 2 * Modelo.comprimento_pista_maxima
                W = 0
            else:
                W = (k / (9)) * Modelo.g
                V = math.sqrt((2 * W) / (Modelo.rho_ar * self.S * self.CL)) * 1.2 * 0.7
                T = Modelo.a * ((V * 0.7) ** 2) + Modelo.b * (V * 0.7) + Modelo.c
                self.Drag = 0.5 * Modelo.rho_ar * V ** 2 * self.S * self.CD
                self.Lift = 0.5 * Modelo.rho_ar * V ** 2 * self.S * self.CL
                Slo = round(
                    (1.44 * (W) ** (2))
                    / (
                        Modelo.g
                        * Modelo.rho_ar
                        * self.S
                        * self.CL
                        * (T - (self.Drag + Modelo.mi_solo * (W - self.Lift)))
                    ),
                    2,
                )

            if Slo > Modelo.comprimento_pista_maxima:
                break

        self.W = W  # MTOW em Newton
        return W

    def calc_carga_paga(self):
        self.MTOW = self.calc_massa()[0]
        self.carga_paga = self.MTOW - self.calc_massa()[1]  # Empirical

    def calc_pontuacao_old(self):
        self.MTOW = self.calc_massa()[0]
        self.carga_paga = self.MTOW - self.calc_massa()[1]  # Empirical
        self.pontuacao = self.carga_paga

    def analisa(self, limpar):
        self.coeficientes(limpar)
        self.mtow()
        self.calc_carga_paga()

    def calc_massa(self):
        MTOW = (self.W / Modelo.g) / Modelo.fator_corretivo  # MTOW em kg
        self.massa_vazia = (1.539331 * ((self.S) ** 2)) + 1.341043 * (self.S)
        return (MTOW, self.massa_vazia)


_asa = Asa()


def limpar_arquivos():
    """
    Deleta os arquivos da pasta
    """
    dirList = os.listdir()
    arquivo = ""
    for file in dirList:
        if (file == "asa.avl") or (file == "resultado.txt") or (file == "comandos.txt"):
            arquivo = file
            os.remove(arquivo)


def calcula_carga_paga(real_env, real_corda, real_offset, limpar=True):
    _asa.setar_geometria(real_env, real_corda, real_offset)
    _asa.analisa(limpar)
    # _asa.salva_asa(gen_no,n)

    global parametros_temp
    parametros_temp = [_asa.S, _asa.CL, _asa.CD, _asa.massa_vazia]

    return _asa.carga_paga


def calcula_lift(real_env, real_corda, real_offset, limpar=True):
    _asa.setar_geometria(real_env, real_corda, real_offset)
    _asa.analisa(limpar)

    global parametros_temp
    parametros_temp = [_asa.S, _asa.CL, _asa.CD, _asa.massa_vazia]

    return _asa.Lift


def calcula_drag(real_env, real_corda, real_offset, limpar=True):
    _asa.setar_geometria(real_env, real_corda, real_offset)
    _asa.analisa(limpar)

    global parametros_temp
    parametros_temp = [_asa.S, _asa.CL, _asa.CD, _asa.massa_vazia]

    return _asa.Drag


def calcula_eficiencia(real_env, real_corda, real_offset, limpar=True):
    _asa.setar_geometria(real_env, real_corda, real_offset)
    _asa.analisa(limpar)

    global parametros_temp
    parametros_temp = [_asa.S, _asa.CL, _asa.CD, _asa.massa_vazia]

    return _asa.Lift / _asa.Drag


def retorna_envergadura(real_env, real_corda, real_offset):
    return 2 * real_env[2]


def retorna_corda_1(real_env, real_corda, real_offset):
    return real_corda[1]


def retorna_corda_2(real_env, real_corda, real_offset):
    return real_corda[2]


def retorna_corda_ponta(real_env, real_corda, real_offset):
    return real_corda[3]


def retorna_delta_envergadura_2(real_env, real_corda, real_offset):
    return real_env[1] - real_env[0]


def retorna_delta_envergadura_3(real_env, real_corda, real_offset):
    return real_env[2] - real_env[1]


def delta_corda_1(real_env, real_corda, real_offset):
    return real_corda[1] - real_corda[0]


def delta_corda_2(real_env, real_corda, real_offset):
    return real_corda[2] - real_corda[1]


def delta_corda_3(real_env, real_corda, real_offset):
    return real_corda[3] - real_corda[2]


def delta_offset2(real_env, real_corda, real_offset):
    return real_offset[1] - real_offset[0]


def delta_offset3(real_env, real_corda, real_offset):
    return real_offset[2] - real_offset[1]


def retorna_parametros():
    return parametros_temp
