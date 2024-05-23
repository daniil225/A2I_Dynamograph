# Математические модели перемещений ПШ
import numpy as np

# Структура данных Параметров характеризующих СК
class SKParam:
    def __init__(self,I = -3353, K = 4928,l = 3734 ,c1 = 3124, c2 = 4013, r = 1346, dh = 0) -> None:
        self.I = I
        self.K = K
        self.l = l
        self.c1 = c1
        self.c2 = c2
        self.r = r
        self.dh = dh
        
        # Предвычесленные параметры 
        self.h = np.sqrt(K**2 - I**2)
        self.r1 = np.sqrt(c1**2 + dh**2)
        self.a = l**2 - self.r1**2 - r**2 + K**2

# Сдвиг по модели в момент положения нижней точки
class PRPos:
    def __init__(self, param:SKParam) -> None:
        self.param = param


    def PRPos_v1(self, phi):
        phi = 90 + phi

        I =  self.param.I
        l =  self.param.l
        c1 = self.param.c1
        c2 = self.param.c2
        r =  self.param.r
        h =  self.param.h
        a =  self.param.a

        b = r*np.sin((phi*np.pi)/180.0) - h
        d = I - r*np.cos((phi*np.pi)/180.0)
        Aa = 1 + (b**2)/(d**2)
        Bb = (a*b)/(d**2) - (2*r*b*np.cos((phi*np.pi)/180.0))/(d) - 2*r*np.sin((phi*np.pi)/180.0)
        Cc = r**2 - l**2 + (a**2)/(4*d**2) - (a*r*np.cos((phi*np.pi)/180.0))/(d)
        D = Bb**2 - 4*Aa*Cc
        y = (-Bb + np.sqrt(D))/(2*Aa)

        PRpos_ = -((c2)/(c1))*(y)/(1000.0)

        return PRpos_


    # Модель Славы
    def PRPos_v2(self, phi):
        phi = 90 - phi

        I =  self.param.I
        l =  self.param.l
        c1 = self.param.c1
        c2 = self.param.c2
        r =  self.param.r
        h =  self.param.h
        a =  self.param.a

        b = r*np.sin((phi*np.pi)/180.0) - h
        d = I - r*np.cos((phi*np.pi)/180.0)
        Aa = 1 + (b**2)/(d**2)
        Bb = (a*b)/(d**2) - (2*r*b*np.cos((phi*np.pi)/180.0))/(d) - 2*r*np.sin((phi*np.pi)/180.0)
        Cc = r**2 - l**2 + (a**2)/(4*d**2) - (a*r*np.cos((phi*np.pi)/180.0))/(d)
        
        PRpos_ = 0
        D = Bb**2 - 4*Aa*Cc
        if D > 0:
            y = (-Bb + np.sqrt(D))/(2*Aa)
            PRpos_ = h/1000.0 - ((c2)/(c1))*(y)/(1000.0)
        else:
            PRpos_ = 0

        return PRpos_

    # Обычная модель как было до этого 
    def PRPos_v3(self, phi):

        I =  self.param.I
        l =  self.param.l
        c1 = self.param.c1
        c2 = self.param.c2
        r =  self.param.r
        h =  self.param.h
        a =  self.param.a

        b = r*np.sin((phi*np.pi)/180.0) - h
        d = I - r*np.cos((phi*np.pi)/180.0)
        Aa = 1 + (b**2)/(d**2)
        Bb = (a*b)/(d**2) - (2*r*b*np.cos((phi*np.pi)/180.0))/(d) - 2*r*np.sin((phi*np.pi)/180.0)
        Cc = r**2 - l**2 + (a**2)/(4*d**2) - (a*r*np.cos((phi*np.pi)/180.0))/(d)
        D = Bb**2 - 4*Aa*Cc
        y = (-Bb + np.sqrt(D))/(2*Aa)

        PRpos_ = ((c2)/(c1))*(y)/(1000.0)

        return PRpos_