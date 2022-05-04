from email.mime import base, image
from lib2to3.pgen2 import grammar
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def get_graph ():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph