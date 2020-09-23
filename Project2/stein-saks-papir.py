import random
from matplotlib import pyplot as plt

# 0 = stein
# 1 = saks
# 2 = papir

class Spiller:

    def __init__(self, navn):
        self.navn = navn

    def velg_aksjon(self): #velger hvilken aksjon som skal utføres
        pass

    def motta_resultat(self, enkeltspill): #vite hva som ble valgt av begge spillere samt hvem som vant
        pass

    def oppgi_navn(self): #oppgir navnet på klassen
        return type(self)



class Tilfeldig(Spiller):

    def __init__(self, navn):
        Spiller.__init__(self, navn)

    def velg_aksjon(self):
        return random.randint(0, 2) #velger tilfeldig om den skal gjøre stein, saks, eller papir.



class Sekvensiell(Spiller):

    def __init__(self,navn):
        Spiller.__init__(self,navn)
        self.siste_aksjon = random.randint(0,2) #starter på et tilfeldig tall
        self.aksjoner = 0

    def velg_aksjon(self): #går sekvensielt gjennom de forskjellige aksjonene
        if self.aksjoner == 0:
            return random.randint(0,2)
        else:
            if self.siste_aksjon == 0:
                neste_aksjon = 1
            if self.siste_aksjon == 1:
                neste_aksjon = 2
            if self.siste_aksjon == 2:
                neste_aksjon = 0
            self.siste_aksjon = neste_aksjon
            self.aksjoner += 1
            return neste_aksjon



class MestVanlig(Spiller): #ser på hva motstanderen har spilt mest, og går ut i fra dette
    def __init__(self, navn):
        Spiller.__init__(self, navn)
        self.motstandersAksjoner = [0, 0, 0]  #[0] = stein, [1] = saks, [2] = papir

    def velg_aksjon(self):
        if self.motstandersAksjoner[0] == self.motstandersAksjoner[1] == self.motstandersAksjoner[2]:
            return random.randint(0,2)
        elif self.motstandersAksjoner[0] > self.motstandersAksjoner[1] and self.motstandersAksjoner[0] == self.motstandersAksjoner[2]:
            return random.choice([1,2])
        elif self.motstandersAksjoner[0] > self.motstandersAksjoner[2] and self.motstandersAksjoner[0] == self.motstandersAksjoner[1]:
            return random.choice([0,2])
        elif self.motstandersAksjoner[2] > self.motstandersAksjoner[0] and self.motstandersAksjoner[2] == self.motstandersAksjoner[1]:
            return random.choice([0,1])
        elif self.motstandersAksjoner[0] > self.motstandersAksjoner[1] and self.motstandersAksjoner[0] > self.motstandersAksjoner[2]:
            return 2
        elif self.motstandersAksjoner[1] > self.motstandersAksjoner[0] and self.motstandersAksjoner[1] > self.motstandersAksjoner[2]:
            return 0
        elif self.motstandersAksjoner[2] > self.motstandersAksjoner[0] and self.motstandersAksjoner[2] > self.motstandersAksjoner[1]:
            return 1


    def motta_resultat(self, enkeltspill): #mottar aksjonen til motspilleren
        if enkeltspill.spiller1 == self:
            motTrekk = enkeltspill.s2
        else:
            motTrekk = enkeltspill.s1
        if motTrekk == 0:
            self.motstandersAksjoner[0] += 1
        elif motTrekk == 1:
            self.motstandersAksjoner[1] += 1
        else:
            self.motstandersAksjoner[2] += 1



class Historiker(Spiller): #Ser hva motstanderen vanligvis spiller etter en viss aksjon
    def __init__(self, name, husk):
        Spiller.__init__(self, name)
        self.alleAksjoner = []
        self.husk = husk


    def velg_aksjon(self):
        if self.husk > len(self.alleAksjoner): #dersom husk er større en antall aksjoner til motstanderen returneres en random aksjon
            return random.randint(0, 2)
        huskListe = self.alleAksjoner[-self.husk:] #ny liste
        antallAksjoner = [0, 0, 0]  #[0] = stein, [1] = saks, [2] = papir
        for i in range(0, len(self.alleAksjoner) - self.husk):
            midListe = self.alleAksjoner[i : i + self.husk]
            indexTilAksjon = i + self.husk
            if huskListe == midListe:
                if self.alleAksjoner[indexTilAksjon] == 0:
                    antallAksjoner[0] += 1
                elif self.alleAksjoner[indexTilAksjon] == 1:
                    antallAksjoner[1] += 1
                else:
                    antallAksjoner[2] += 1
        etterfølger = antallAksjoner.index(max(antallAksjoner)) #ser hva motstanderen vanlivis spiller etter det han spilte sist, og velger aksjon ut i fra det
        if etterfølger == 0:
            return 2
        elif etterfølger == 1:
            return 0
        elif etterfølger == 2:
            return 1


    def motta_resultat(self, enkeltspill):
        if enkeltspill.spiller1 == self:
            motstandersAksjon = enkeltspill.s2
        else:
            motstandersAksjon = enkeltspill.s1
        self.alleAksjoner.append(motstandersAksjon) #legger til aksjonen til motstanderen i listen over alle aksjonene



class Aksjon:
    def __init__(self, move):
        self.move = move

    def __eq__(self, other): #Ser om alsjonene er like
        return self.move == other

    def __gt__(self, other):
        if (self.move == 0 and other == 1) or (self.move == 1 and other == 2) or (self.move == 2 and other == 0): #ser om aksjonene vil slå hverandre
            return True
        return False


class Enkeltspill(object):
    def __init__(self, spiller1, spiller2):
        self.spiller1 = spiller1
        self.spiller2 = spiller2
        self.vinner = None
        self.s1 = None
        self.s2 = None


    def gjennomfore_spill(self):
        self.s1 = self.spiller1.velg_aksjon() #spiller 1 velger aksjon
        self.s2 = self.spiller2.velg_aksjon()  #spiller 2 velger aksjon
        self.spiller1.motta_resultat(self) #spiller 1 mottar resultatet
        self.spiller2.motta_resultat(self) #spiller 2 mottar resutatet
        aksjon1 = Aksjon(self.s1) #ser hva spiller 1 spilte
        aksjon2 = Aksjon(self.s2) #ser hva spiller 2 spilte
        if aksjon1 == aksjon2:
            return 0 #uavgjort
        elif aksjon1 > aksjon2:
            self.vinner = self.spiller1
            return 1 #spiller 1 vant
        else:
            self.vinner = self.spiller2
            return 2 #spiller 2 vant

    @staticmethod
    def aksjon(aksjon): #gjør __str__ metoden kortere
        if aksjon == 0:
            return "Stein"
        elif aksjon == 1:
            return "Saks"
        elif aksjon == 2:
            return "Papir"

    def __str__(self):
        s1 = self.spiller1.navn + ":\t" + self.aksjon(self.s1)
        s2 = self.spiller2.navn + ":\t" + self.aksjon(self.s2)
        if self.vinner is None:
            return s1 + '\t\tDRAW' + '\n' + s2 + '\t\tDRAW' + '\n'
        elif self.vinner == self.spiller1:
            return s1 + '\t\tWIN' + '\n' + s2 + '\n'
        else:
            return s1 + '\n' + s2 + '\t\tWIN' + '\n'


class MangeSpill:
    def __init__(self, spiller1, spiller2, n_games):
        self.games = n_games
        self.spiller1 = spiller1
        self.spiller2 = spiller2
        self.poengSpiller1 = 0
        self.poengSpiller2 = 0
        self.game = 1
        self.gevinstSpiller1 = [0]
        self.gevinstSpiller2 = [0]

    def arranger_enkeltspill(self):
        game = Enkeltspill(self.spiller1, self.spiller2) #setter opp et enkeltspill
        match = game.gjennomfore_spill() #starter enkeltspillet
        print(str(self.game) + ": ") #viser hvilket nr. i rekken spillet er
        print(game)
        self.game += 1
        if match == 0: #uavgjort
            self.poengSpiller1 += 0.5
            self.poengSpiller2 += 0.5
        elif match == 1: #spiller 1 vinner
            self.poengSpiller1 += 1
        else: #spiller 2 vinner
            self.poengSpiller2 += 1
        self.gevinstSpiller1.append(self.poengSpiller1 / (self.game - 1)) #ser hvem som vinner mest (antall poeng/spill spilt)
        self.gevinstSpiller2.append(self.poengSpiller2 / (self.game - 1))

    def arranger_turnering(self):
        while self.games > 0: #arrangerer så mange enkeltspill som oppgitt
            self.arranger_enkeltspill()
            self.games -= 1
        print(self)
        plt.plot(self.gevinstSpiller1, label=self.spiller1.navn, color='r') #plotter grafen til spiller 1
        plt.plot(self.gevinstSpiller2, label=self.spiller2.navn, color='g') #plotter grafen til spiller 2
        plt.ylim([0, 1])
        plt.ylabel("Poeng i prosent")
        plt.xlabel("Antall spill")
        plt.legend(loc='best')
        plt.grid()
        plt.show()

    def __str__(self):
        s1p = "{0:.2f}".format(self.poengSpiller1 / self.game * 100.0)
        s2p = "{0:.2f}".format(self.poengSpiller2 / self.game * 100.0)
        str1 = self.spiller1.navn + '\t\t' + s1p + '%\n'
        str2 = self.spiller2.navn + '\t' + s2p + '%\n'
        return str1 + str2


def main():
    spiller1 = Tilfeldig("Seline")
    spiller2 = Sekvensiell("Andrine")
    spiller3 = Historiker("Christina", 3)
    spiller4 = MestVanlig("Ingvild")

    spill = MangeSpill(spiller2, spiller3, 100)
    spill.arranger_turnering()
    print(spill)

main()