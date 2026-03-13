R = 8.31446261815324

# While loop zur Wiederholung
while True:																	
    print("\nZustandsänderung eines idealen Gases wählen:")
    zustand = input("(IT=isotherm, IB=isobar, IC=isochor): ").upper()

    #Zustandsauswahl Isotherm
    if zustand == "IT":	
        p1 = float(input("Druck p (Bar): "))
        V1 = float(input("Volumen V (m^3): "))
        T = p1 * V1
        print("Konstante Temperatur:", T,"K")

        wahl = input("p oder V ändern?: ").lower()
        if wahl == "p":
            p2 = float(input("Neuer Druck: "))
            print("Neues Volumen =", T / p2, "m^3")
        elif wahl == "v":
            V2 = float(input("Neues Volumen: "))
            print("Neuer Druck =", T / V2, "Bar")
            
    #Zustandsauswahl Isobar
    elif zustand == "IB":
        T1 = float(input("Temperatur T (K): "))
        V1 = float(input("Volumen V (m^3): "))
        p = V1 / T1
        print("Konstanter Druck:", p," Bar")

        wahl = input("T oder V ändern?: ").upper()
        if wahl == "T":
            T2 = float(input("Neue Temperatur: "))
            print("Neues Volumen =", T2 * p, "m^3")
        elif wahl == "V":
            V2 = float(input("Neues Volumen: "))
            print("Neue Temperatur =", V2 / p, "K")
            
    #Zustandsauswahl Isochor
    elif zustand == "IC":
        T1 = float(input("Temperatur T (K): "))
        p1 = float(input("Druck p (Bar): "))
        V = p1 / T1
        print("Konstantes Volumen:", V, "m^3")

        wahl = input("T oder p ändern?: ").upper()
        if wahl == "T":
            T2 = float(input("Neue Temperatur: "))
            print("Neuer Druck =", T2 * V, "Bar")
        elif wahl == "P":
            p2 = float(input("Neuer Druck: "))
            print("Neue Temperatur =", p2 / V, "K")
            
    # While loop breaker
    if input("\nNochmal? (x zum Beenden): ").lower() == "x":
        break
exit()     