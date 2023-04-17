# Defines all farm animals as a class with attributes for manure production, manure composition, manure properties such as energy value, time in and out of stable, etc.

class Animal:
    manure_l = 0  # amount of liquid manure [kg] produced by 1 animal per year (assumption of density = 1'000 kg / m^3)
    manure_l_tot = 0 # amount of liquid manure [kg] produced by all animals per year (assumption of density = 1'000 kg / m^3)
    manure_s = 0  # amount of solid manure [kg] produced by 1 animal per year
    manure_s_tot = 0 # amount of solid manure [kg] produced by all animals per year
    manure_straw = 0  # amount of straw [kg] used by 1 animal per year
    manure_straw_tot = 0 # amount of straw [kg] used by all animals per year
    manure_methane_s = 0  # Theoretical Methane potential of 1 kg of solid manure in [NL/kg odw]
    manure_methane_l = 0  # Theoretical Methane potential of 1 kg of liguid manure in [NL/kg odw]
    manure_methane_straw = 0  # Theoretical Methane potential of 1 kg of straw in [NL/kg odw]
    manure_n = 0  # total N in waste per Animal and year [kg/y]
    manure_p = 0  # total P in waste per Animal and year [kg/y]
    manure_k = 0  # total K in waste per Animal and year [kg/y]
    manure_dw_l = 0  # dry weight percentage of the liquid part of manure
    manure_odw_l = 0  # organic fraction of the dry weight in percent
    manure_dw_s = 0  # dry weight percentage of the solid part of manure
    manure_odw_s = 0  # organic fraction of the dry weight in percent
    methane_pot_l = 0   # potential methane produced from collected liquid manure [NL]
    methane_pot_s = 0   # potential methane produced from collected solid manure [NL]
    methane_pot_tot = 0
    n_tot = 0   # total N in collected manure
    p_tot = 0   # total P in collected manure
    k_tot = 0   # total K in collected manure
    def __init__(self, amount, d_out, hr_out, stable_type):
        self.amount = amount  # number of animals
        self.hr_out = hr_out  # hours per day outside of stable
        self.d_out = d_out  # days per year outside of stable
        self.stable_type = stable_type  # type of stable used, 0= nur Gülle 1=Gülle/Mist 2=Nur Mist
        self.manure_frac_d = (24 - self.hr_out) / 24  # fraction of the manure collected on days the animal is outside of the stable
        self.manure_frac_y = 1 - self.manure_frac_d * self.d_out / 365  # fraction of the year spent in the stable, where manure can be collected

             # potential methane produced in 1 year from collected manure
    def methane_pot(self):
        self.methane_pot_l = self.amount * self.manure_l * self.manure_dw_l * self.manure_odw_l * self.manure_methane_l * self.manure_frac_y
        self.methane_pot_s = self.amount * self.manure_s * self.manure_dw_s * self.manure_odw_s * self.manure_methane_s * self.manure_frac_y
        self.methane_pot_tot = self.methane_pot_l + self.methane_pot_s

                # total amount of nutrients in collected manure
    def nutrients(self):
        self.n_tot = self.amount * self.manure_n * self.manure_frac_y
        self.p_tot = self.amount * self.manure_p * self.manure_frac_y
        self.k_tot = self.amount * self.manure_k * self.manure_frac_y

    def manure_prod_tot(self):
        self.manure_l_tot = self.amount * self.manure_l * self.manure_frac_y
        self.manure_s_tot = self.amount * self.manure_s * self.manure_frac_y
        self.manure_straw_tot = self.amount * self.manure_straw * self.manure_frac_y


class Cow(Animal):

    manure_dw_l = 0.08  # assumption dw and odw fractions are all roughly the same for all kinds of cows
    manure_dw_s = 0.2
    manure_odw_l = 0.75
    manure_odw_s = 0.8
    manure_methane_l = 340  # assumption methane yield per kg odw is the same for all cow manure
    manure_methane_s = 355


class Milchkuh(Cow):

    def manure_prod(self):
        if self.stable_type == 0:  # attributes for stabling whith only liquid manure
            self.manure_l = 23000

        elif self.stable_type == 1:  # attributes for stabling mixed liquid and solids
            self.manure_l = 11000
            self.manure_s = 8900
            self.manure_straw = 6800

        else:  # attributes for stabling only solid manure
            self.manure_s = 21000
            self.manure_straw = 30000

        self.manure_n = 112
        self.manure_p = 17
        self.manure_k = 143



class Mutterkuh(Cow):  # assumption of "mittelschwere Rassen" as an average

    def manure_prod(self):
        if self.stable_type == 0:  # attributes for stabling whith only liquid manure
            self.manure_l = 17000

        elif self.stable_type == 1:  # attributes for stabling mixed liquid and solids
            self.manure_l = 8700
            self.manure_s = 6700
            self.manure_straw = 5000

        else:  # attributes for stabling only solid manure
            self.manure_s = 16000
            self.manure_straw = 25000

        self.manure_n = 85
        self.manure_p = 12
        self.manure_k = 117


class Aufzuchtrind(Cow):  # assumption all are 1-2 years old as an average
    def manure_prod(self):
        if self.stable_type == 0:  # attributes for stabling whith only liquid manure
            self.manure_l = 8000

        elif self.stable_type == 1:  # attributes for stabling mixed liquid and solids
            self.manure_l = 4000
            self.manure_s = 3200
            self.manure_straw = 2500

        else:  # attributes for stabling only solid manure
            self.manure_s = 7600
            self.manure_straw = 12000

        self.manure_n = 40
        self.manure_p = 5.7
        self.manure_k = 50


class Mastkalb(Cow):  # amount in "Anzahl Tierplätze" not in "Anzahl gemästeter Tiere"
    def manure_prod(self):
        self.manure_s = 3200
        self.manure_straw = 4200

        self.manure_n = 18
        self.manure_p = 3.1
        self.manure_k = 9.4


class Mutterkuhkalb(Cow):       #assumption up to 350kg and per animal
    def manure_prod(self):
        if self.stable_type == 0:  # attributes for stabling whith only liquid manure
            self.manure_l = 4100

        elif self.stable_type == 1:  # attributes for stabling mixed liquid and solids
            self.manure_l = 2000
            self.manure_s = 1600
            self.manure_straw = 1300

        else:  # attributes for stabling only solid manure
            self.manure_s = 3800
            self.manure_straw = 4200

        self.manure_n = 22
        self.manure_p = 3.1
        self.manure_k = 20


class RiendviehMast(Cow):   #Assumption older than 160 days
    def manure_prod(self):
        if self.stable_type == 0:  # attributes for stabling whith only liquid manure
            self.manure_l = 10000

        #elif self.stable_type == 1:  # attributes for stabling mixed liquid and solids
         #   self.manure_l = 4000
          #  self.manure_s = 3200
           # self.manure_straw = 2500

        else:  # attributes for stabling only solid manure
            self.manure_s = 11000
            self.manure_straw = 16000

        self.manure_n = 49
        self.manure_p = 5.7
        self.manure_k = 34


class Zuchtstier(Cow):          #no differentiation of manure production, so assumption is it's the same as Mutterkuh schwer
    def manure_prod(self):
        if self.stable_type == 0:  # attributes for stabling whith only liquid manure
            self.manure_l = 19000

        elif self.stable_type == 1:  # attributes for stabling mixed liquid and solids
            self.manure_l = 9400
            self.manure_s = 7600
            self.manure_straw = 5000

        else:  # attributes for stabling only solid manure
            self.manure_s = 18000
            self.manure_straw = 25000

        self.manure_n = 50
        self.manure_p = 7.9
        self.manure_k = 70


class Pig(Animal):  #assumption only liquid manure for pigs
    manure_dw_l = 0.06  # assumption dw and odw fractions are all roughly the same for all kinds of pigs
    manure_odw_l = 0.74
    manure_methane_l = 411  # assumption methane yield per kg odw is the same for all pig manure



class Mastschwein(Pig): #per animalspot (Platz)
    def manure_prod(self):
        self.manure_l = 1600
        self.manure_n = 3.9
        self.manure_p = 0.7
        self.manure_k = 1.5


class Zuchtschweineplatz(Pig):
    def manure_prod(self):
        self.manure_l = 7500
        self.manure_n = 44
        self.manure_p = 9.2
        self.manure_k = 19





class Poultry(Animal): #assume always Bodenhaltung for 1 animal, not 100
    manure_dw_s = 0.53  # assumption dw and odw fractions are all roughly the same for all kinds of poultry
    manure_odw_s = 0.78
    manure_methane_s = 259  # assumption methane yield per kg odw is the same for all poultry manure


class Legehenne(Poultry):
    def manure_prod(self):
        self.manure_s = 15
        self.manure_n = 0.8
        self.manure_p = 0.2
        self.manure_k = 0.25


class Junghenne(Poultry):
    def manure_prod(self):
        self.manure_s = 6
        self.manure_n = 0.3
        self.manure_p = 0.074
        self.manure_k = 0.1


class Mastpoulet(Poultry):
    def manure_prod(self):
        self.manure_s = 8
        self.manure_n = 0.36
        self.manure_p = 0.06
        self.manure_k = 0.18
