# import Estimação_de_massa as est
import analise

class asa():
    def __init__(self, B, cordas, offsets, alfa_stol = 13.5):
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
        self.g = 9.81
        self.rho = 1.225
        self.mi = 0.025
        self.pista_total = 90

    def file_and_commands(self, alfa_stol = 13.5): # Não mexer nisso~
        analise.file_and_commands(self,alfa_stol)
        
    def coeficientes(self, angulo):
        analise.coeficientes(self, angulo)
    
    def lift (self, V, rho = 1.225 ):
        return (self.rho*V**(2)*0.5*self.CL*self.S)
    
    def drag (self, V, rho = 1.225 ):
        return (self.rho*V**(2)*0.5*self.CD*self.S)

    def mtow (self, rho = 1.225, coeficientes = (-0.0126, -0.5248, 40.0248)):
        return analise.mtow(self, rho, coeficientes)
    
    def calc_massa(self, metodo_massa):
        return analise.calc_massa(self, metodo_massa)
        
    def calc_pontuacao (self, metodo_massa):
        self.MTOW = self.calc_massa(metodo_massa)[0]
        self.carga_paga = (self.MTOW - self.calc_massa(metodo_massa)[1]) # Empirical
        self.pontuacao = self.carga_paga
                
    def analisa(self, metodo_massa = 'MTOW'):
        analise.analisa(self, metodo_massa)