from math import sqrt, pi
### Gegeben
V_dot_gal_h = 31.5 # in USgal/h bei def. Druck Differenz
delta_p_psi = 100 # in psi
rho_oel = 780 # in kg/m^3

### Annahme
Cd = 0.6

### Konvertierungstools

def psi_to_pa(p_psi):
    return p_psi * 6894.76

def USgal_to_m3(V_gal):
    return V_gal / 264.172

### Berechnung
# Formula
# m_dot = rho * A * Cd * sqrt(2 * delta_p)
# V_dot = A * Cd * sqrt(2 * delta_p) 

V_dot_m3_s = USgal_to_m3(V_dot_gal_h) / 3600
A_Cd = V_dot_m3_s / sqrt(2 * psi_to_pa(delta_p_psi) / rho_oel)

# Ausgabe:
A = A_Cd / Cd
D = sqrt(4 * A / pi)
print(f"Cd * A = {A_Cd} m²")
print(f"bei Cd = {Cd} entspricht dies A = {A_Cd / Cd} m² bzw. D = {D * 1000} mm")