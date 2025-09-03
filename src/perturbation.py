import numpy as np
import matplotlib.pyplot as plt

def mandelbrot_perturbation(reference_c, delta_c, max_iter):
    """
    Berechnet die Mandelbrot-Menge mit dem Perturbationsalgorithmus.
    
    :param reference_c: Referenzpunkt in der komplexen Ebene.
    :param delta_c: Perturbation (Abweichung) vom Referenzpunkt.
    :param max_iter: Maximale Anzahl an Iterationen.
    :return: Anzahl der Iterationen bis zur Divergenz.
    """
    # Initialisierung
    z_ref = 0
    z_delta = 0
    for n in range(max_iter):
        # Berechnung der Referenzbahn
        z_ref = z_ref**2 + reference_c
        
        # Berechnung der Perturbation
        z_delta = 2 * z_ref * z_delta + delta_c
        
        # Prüfen auf Divergenz
        if abs(z_ref + z_delta) > 2:
            return n
    return max_iter

def mandelbrot_set_perturbation(xmin, xmax, ymin, ymax, width, height, max_iter):
    """
    Generiert die Mandelbrot-Menge mit dem Perturbationsalgorithmus.
    
    :param xmin, xmax, ymin, ymax: Bereich der komplexen Ebene.
    :param width, height: Auflösung des Bildes.
    :param max_iter: Maximale Anzahl an Iterationen.
    :return: 2D-Array mit Iterationswerten.
    """
    x = np.linspace(xmin, xmax, width)
    y = np.linspace(ymin, ymax, height)
    mandelbrot_image = np.empty((height, width))
    
    # Wähle einen Referenzpunkt (z. B. die Mitte des Bildes)
    reference_c = (xmin + xmax) / 2 + 1j * (ymin + ymax) / 2
    
    for i in range(height):
        for j in range(width):
            # Berechne die Perturbation relativ zum Referenzpunkt
            delta_c = x[j] + 1j * y[i] - reference_c
            mandelbrot_image[i, j] = mandelbrot_perturbation(reference_c, delta_c, max_iter)
    
    return mandelbrot_image

# Parameter für die Mandelbrot-Menge
xmin, xmax, ymin, ymax = -2.0, 1.0, -1.5, 1.5
width, height = 1000, 1000
max_iter = 100

# Mandelbrot-Menge berechnen
mandelbrot_image = mandelbrot_set_perturbation(xmin, xmax, ymin, ymax, width, height, max_iter)

# Plotten der Mandelbrot-Menge
plt.figure(figsize=(10, 10))
plt.imshow(mandelbrot_image, extent=(xmin, xmax, ymin, ymax), cmap='hot')
plt.colorbar(label='Iterationen bis zur Divergenz')
plt.title('Mandelbrot-Menge (Perturbationsalgorithmus)')
plt.xlabel('Re(z)')
plt.ylabel('Im(z)')
plt.show()