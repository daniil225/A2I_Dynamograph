from Core.ContollErrorCalc import ContollErrorCalc
import numpy as np

#f = ContollErrorCalc()

# Параметры ДУ колебаний 
class ParamDE:
    def __init__(self, T, H = 24, E=2.1*10**11, a = 4.98*10**3, g = 9.81) -> None:
        """
        T - Период качания [сек]
        E - Модуль Юнга упругости материала штанг [Па]
        a - Скорость звука [м/с]
        H - Количество гармоник [-] 
        """
        self.T = T # Период качания 
        self.E = E # Модуль Юнга 
        self.a = a # Скорость звука
        self.H = H # Количество гармоник 
        self.g = g # Ускорение свободного падения 
        self.N = 200 # Количество точек динамограммы 

        self.Ts = T/(self.N-1) # Шаг по времени


class DESolver:
    def __init__(self, param:ParamDE) -> None:
        self.param = param
       
        # Коэффициенты ряда Фурье  
        self.alpha = []
        self.beta =  []
        self.sigma = []
        self.tau =   []
        self.nu =    []
        self.delta = []
    
    def InitSec0(self, gamma, w, L, N, Fdyn, X):
        c = np.pi*self.param.a*(gamma/(2*L))

        for p in range(0, self.param.H + 1):
            
            if p == 0:
                self.alpha.append(0)
                self.beta.append(0)
            else:
                alpha1 = (p*w)/(self.param.a*np.sqrt(2))*np.sqrt(1 + np.sqrt(1 + (c/(p*w))**2))
                beta1 = (p*w)/(self.param.a*np.sqrt(2))*np.sqrt(-1 + np.sqrt(1 + (c/(p*w))**2))
                self.alpha.append(alpha1)
                self.beta.append(beta1)

            sigma1,tau1,nu1,delta1 = 0,0,0,0
            g = self.param.g
            for k in range(0, N):
                sigma1 += g*Fdyn[k]*np.cos((2*np.pi*p*k)/(N))
                tau1 += g*Fdyn[k]*np.sin((2*np.pi*p*k)/(N))
                nu1 += X[k]*np.cos((2*np.pi*p*k)/(N))
                delta1 += X[k]*np.sin((2*np.pi*p*k)/(N))

            sigma1 = 2*sigma1/N
            tau1 = 2*tau1/N
            nu1 = 2*nu1/N
            delta1 = 2*delta1/N

            self.sigma.append(sigma1)
            self.tau.append(tau1)
            self.nu.append(nu1)
            self.delta.append(delta1)

    def SectionFunction(self, w, L, Sq):
        k = []
        mu = []
        O = [0]
        P = [0]
        dO = [0]
        dP = [0]

        nu_out = [0]
        delta_out = [0]
        sigma_out = [0]
        tau_out = [0]
        
        Uout = []
        FOut = []
        
        for q in range(1, self.param.H + 1):
            k1  = (self.sigma[q]*self.alpha[q] + self.tau[q]*self.beta[q])/(self.param.E*Sq*(self.alpha[q]**2 + self.beta[q]**2))            
            mu1 = (self.sigma[q]*self.beta[q] - self.tau[q]*self.alpha[q])/(self.param.E*Sq*(self.alpha[q]**2 + self.beta[q]**2))
            O1 = (-k1*np.cosh(self.beta[q]*L) + self.delta[q]*np.sinh(self.beta[q]*L))*np.sin(self.alpha[q]*L) + (-mu1*np.sinh(self.beta[q]*L) + self.nu[q]*np.cosh(self.beta[q]*L))*np.cos(self.alpha[q]*L)
            P1 = (-k1*np.sinh(self.beta[q]*L) + self.delta[q]*np.cosh(self.beta[q]*L))*np.cos(self.alpha[q]*L) - (-mu1*np.cosh(self.beta[q]*L) + self.nu[q]*np.sinh(self.beta[q]*L))*np.sin(self.alpha[q]*L)
            dO1 = ((self.tau[q]/(Sq*self.param.E))*np.sinh(self.beta[q]*L) - (self.delta[q]*self.beta[q] - self.nu[q]*self.alpha[q])*np.cosh(self.beta[q]*L) )*np.sin(self.alpha[q]*L) + ((self.sigma[q]/(Sq*self.param.E))*np.cosh(self.beta[q]*L) - (self.nu[q]*self.beta[q] + self.delta[q]*self.alpha[q])*np.sinh(self.beta[q]*L))*np.cos(self.alpha[q]*L)
            dP1 = ((self.tau[q]/(Sq*self.param.E))*np.cosh(self.beta[q]*L) - (self.delta[q]*self.beta[q] - self.nu[q]*self.alpha[q])*np.sinh(self.beta[q]*L) )*np.cos(self.alpha[q]*L) - ((self.sigma[q]/(Sq*self.param.E))*np.sinh(self.beta[q]*L) - (self.nu[q]*self.beta[q] + self.delta[q]*self.alpha[q])*np.cosh(self.beta[q]*L))*np.sin(self.alpha[q]*L)
            
            O.append(O1)
            P.append(P1)
            dO.append(dO1)
            dP.append(dP1)

            nu_out.append(O1)
            delta_out.append(P1)
            sigma_out.append(Sq*self.param.E*dO1)
            tau_out.append(Sq*self.param.E*dP1)

        for i in range(0, self.param.N):
            ti = i*self.param.Ts
            U = (self.sigma[0]*L)/(2*self.param.E*Sq) + self.nu[0]/2
            F = (self.sigma[0])/(2*self.param.g)

            for j in range(1, self.param.H + 1):
                U += O[j]*np.cos(j*w*ti) + P[j]*np.sin(j*w*ti)
                F += ((Sq*self.param.E)/(self.param.g))*(dO[j]*np.cos(j*w*ti) + dP[j]*np.sin(j*w*ti))

            Uout.append(U)
            FOut.append(F)
        
        nu_out[0] = (L*self.sigma[0])/(Sq*self.param.E) + self.nu[0]
        sigma_out[0] = self.sigma[0]

        # Копия результата пересчета коэффициентов 
        self.sigma = sigma_out.copy()
        self.nu = nu_out.copy()
        self.delta = delta_out.copy()
        self.tau = tau_out.copy()
        
        # Возврат Усилие/Перемещение 
        return FOut, Uout



class ControllErrorDESolver:
    def __init__(self, param:ParamDE, f_sin_N = 512, f_cos_N = 512, f_sinh_N = 512, f_cosh_N = 512, f_sqrt_N = 512) -> None:

        # Инициализация функций расчета с приближением
        self.f_sin_N = f_sin_N
        self.f_sin_T = 2*np.pi
        self.f_sin:ContollErrorCalc = ContollErrorCalc(np.sin, self.f_sin_N, self.f_sin_T)

        self.f_cos_N = f_cos_N
        self.f_cos_T = 2*np.pi
        self.f_cos:ContollErrorCalc = ContollErrorCalc(np.cos, self.f_cos_N, self.f_cos_T)

        self.f_sinh_T = 3
        self.f_sinh_N = f_sinh_N
        self.f_sinh:ContollErrorCalc = ContollErrorCalc(np.sinh, self.f_sinh_N, self.f_sinh_T)

        self.f_cosh_T = 3
        self.f_cosh_N = f_cosh_N
        self.f_cosh:ContollErrorCalc = ContollErrorCalc(np.cosh, self.f_cosh_N, self.f_cosh_T)

        self.f_sqrt_T = 5
        self.f_sqrt_N = f_sqrt_N
        self.f_sqrt:ContollErrorCalc = ContollErrorCalc(np.sqrt, self.f_sqrt_N, self.f_sqrt_T)

        self.param:ParamDE = param
       
        # Коэффициенты ряда Фурье  
        self.alpha = []
        self.beta =  []
        self.sigma = []
        self.tau =   []
        self.nu =    []
        self.delta = []

        

    def InitSec0(self, gamma, w, L, N, Fdyn, X):
        c = np.pi*self.param.a*(gamma/(2*L))

        for p in range(0, self.param.H + 1):
            
            if p == 0:
                self.alpha.append(0)
                self.beta.append(0)
            else:
                alpha1 = (p*w)/(self.param.a*np.sqrt(2))*self.f_sqrt.Calc(1 + np.sqrt(1 + (c/(p*w))**2))
                beta1 = (p*w)/(self.param.a*np.sqrt(2))*self.f_sqrt.Calc(-1 + self.f_sqrt.Calc(1 + (c/(p*w))**2))
                self.alpha.append(alpha1)
                self.beta.append(beta1)

            sigma1,tau1,nu1,delta1 = 0,0,0,0
            g = self.param.g
            for k in range(0, N):
                sigma1 += g*Fdyn[k]*self.f_cos.Calc((2*np.pi*p*k)/(N))
                tau1 += g*Fdyn[k]*self.f_sin.Calc((2*np.pi*p*k)/(N))
                nu1 += X[k]*self.f_cos.Calc((2*np.pi*p*k)/(N))
                delta1 += X[k]*self.f_sin.Calc((2*np.pi*p*k)/(N))

            sigma1 = 2*sigma1/N
            tau1 = 2*tau1/N
            nu1 = 2*nu1/N
            delta1 = 2*delta1/N

            self.sigma.append(sigma1)
            self.tau.append(tau1)
            self.nu.append(nu1)
            self.delta.append(delta1)

    def SectionFunction(self, w, L, Sq):
        k = []
        mu = []
        O = [0]
        P = [0]
        dO = [0]
        dP = [0]

        nu_out = [0]
        delta_out = [0]
        sigma_out = [0]
        tau_out = [0]
        
        Uout = []
        FOut = []
        
        for q in range(1, self.param.H + 1):
            k1  = (self.sigma[q]*self.alpha[q] + self.tau[q]*self.beta[q])/(self.param.E*Sq*(self.alpha[q]**2 + self.beta[q]**2))            
            mu1 = (self.sigma[q]*self.beta[q] - self.tau[q]*self.alpha[q])/(self.param.E*Sq*(self.alpha[q]**2 + self.beta[q]**2))
            O1 = (-k1*self.f_cosh.Calc(self.beta[q]*L) + self.delta[q]*self.f_sinh.Calc(self.beta[q]*L))*self.f_sin.Calc(self.alpha[q]*L) + (-mu1*self.f_sinh.Calc(self.beta[q]*L) + self.nu[q]*self.f_cosh.Calc(self.beta[q]*L))*self.f_cos.Calc(self.alpha[q]*L)
            P1 = (-k1*self.f_sinh.Calc(self.beta[q]*L) + self.delta[q]*self.f_cosh.Calc(self.beta[q]*L))*self.f_cos.Calc(self.alpha[q]*L) - (-mu1*self.f_cosh.Calc(self.beta[q]*L) + self.nu[q]*self.f_sinh.Calc(self.beta[q]*L))*self.f_sin.Calc(self.alpha[q]*L)
            dO1 = ((self.tau[q]/(Sq*self.param.E))*self.f_sinh.Calc(self.beta[q]*L) - (self.delta[q]*self.beta[q] - self.nu[q]*self.alpha[q])*self.f_cosh.Calc(self.beta[q]*L) )*self.f_sin.Calc(self.alpha[q]*L) + ((self.sigma[q]/(Sq*self.param.E))*self.f_cosh.Calc(self.beta[q]*L) - (self.nu[q]*self.beta[q] + self.delta[q]*self.alpha[q])*self.f_sinh.Calc(self.beta[q]*L))*self.f_cos.Calc(self.alpha[q]*L)
            dP1 = ((self.tau[q]/(Sq*self.param.E))*self.f_cosh.Calc(self.beta[q]*L) - (self.delta[q]*self.beta[q] - self.nu[q]*self.alpha[q])*self.f_sinh.Calc(self.beta[q]*L) )*self.f_cos.Calc(self.alpha[q]*L) - ((self.sigma[q]/(Sq*self.param.E))*self.f_sinh.Calc(self.beta[q]*L) - (self.nu[q]*self.beta[q] + self.delta[q]*self.alpha[q])*self.f_cosh.Calc(self.beta[q]*L))*self.f_sin.Calc(self.alpha[q]*L)
            
            O.append(O1)
            P.append(P1)
            dO.append(dO1)
            dP.append(dP1)

            nu_out.append(O1)
            delta_out.append(P1)
            sigma_out.append(Sq*self.param.E*dO1)
            tau_out.append(Sq*self.param.E*dP1)

        for i in range(0, self.param.N):
            ti = i*self.param.Ts
            U = (self.sigma[0]*L)/(2*self.param.E*Sq) + self.nu[0]/2
            F = (self.sigma[0])/(2*self.param.g)

            for j in range(1, self.param.H + 1):
                U += O[j]*self.f_cos.Calc(j*w*ti) + P[j]*self.f_sin.Calc(j*w*ti)
                F += ((Sq*self.param.E)/(self.param.g))*(dO[j]*self.f_cos.Calc(j*w*ti) + dP[j]*self.f_sin.Calc(j*w*ti))

            Uout.append(U)
            FOut.append(F)
        
        nu_out[0] = (L*self.sigma[0])/(Sq*self.param.E) + self.nu[0]
        sigma_out[0] = self.sigma[0]

        # Копия результата пересчета коэффициентов 
        self.sigma = sigma_out.copy()
        self.nu = nu_out.copy()
        self.delta = delta_out.copy()
        self.tau = tau_out.copy()
        
        # Возврат Усилие/Перемещение 
        return FOut, Uout

