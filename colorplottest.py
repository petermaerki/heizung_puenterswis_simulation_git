import matplotlib.pyplot as plt
import numpy as np

from util_common import SAVEFIG_KWARGS

"""
# Fixing random state for reproducibility
np.random.seed(19680801)

Z = np.random.rand(6, 10)

# fig, (ax0, ax1) = plt.subplots(2, 1)
fig, ax0 = plt.subplots()
c = ax0.pcolor(Z)
ax0.set_title("default: no edges")

cbar = fig.colorbar()
cbar.set_label("ZLabel", loc="top")

fig.tight_layout()
plt.show()

"""
# https://www.statology.org/matplotlib-contour-plot/
x = np.linspace(0, 24, 5)
y = np.linspace(0, 1, 3)

X, Y = np.meshgrid(x, y)
Z = ((np.sin(X * 2 + Y) + 1) * 3 + (np.cos(Y + 5) + 1)) * 7

min = 10
max = 80
levels = np.linspace(min, max, max - min + 1)

# plt.contourf(X, Y, Z, levels, cmap="turbo")  # "Reds", 'coolwarm',"plasma"
plt.contourf(X, Y, Z, levels, cmap="turbo")  # "Reds", 'coolwarm',"plasma"
plt.colorbar(ticks=range(10, 90, 10), label="Temperatur C")
plt.yticks([0, 1], ("unten", "oben"))

plt.savefig(
    "C:/data/peters_daten\haus_13_zelglistrasse_49/heizung/heizung_peter_schaer_siedlung/heizung_puenterswis_simulation_git/pictures/energiereserve_"
    + ".png",
    **SAVEFIG_KWARGS
)

plt.show()


print(Z)
