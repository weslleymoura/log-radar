import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st
from .den_stream.DenStream import *
from .utils import get_graph
from django.db.models import IntegerField, Value

def plot_clusters (clusterer):

    # Selecting clustering center and radius
    cluster_center = []
    cluster_radius = []
    for cluster in clusterer.p_micro_clusters:
        cluster_center.append(cluster.center())
        cluster_radius.append(cluster.radius())

    cluster_center = np.array(cluster_center)
    cluster_radius = np.array(cluster_radius)

    # Selecting clustering center and radius (outlier clusters)
    o_cluster_center = []
    o_cluster_radius = []
    for cluster in clusterer.o_micro_clusters:
        o_cluster_center.append(cluster.center())
        o_cluster_radius.append(cluster.radius())

    o_cluster_center = np.array(o_cluster_center)
    o_cluster_radius = np.array(o_cluster_radius)

    # visualize
    fig, ax = plt.subplots(figsize=(10,5))
    #plt.switch_backend('AGG')
    #plt.plot(df_train.x, df_train.y, ".b", markersize=6)
    plt.plot(cluster_center[:, 0], cluster_center[:, 1], ".b", markersize=15)

    if len(o_cluster_center) > 0:
        plt.plot(o_cluster_center[:, 0], o_cluster_center[:, 1], ".r", markersize=15)

    for idx in range(len(cluster_center)):
        circle = plt.Circle((cluster_center[idx, 0], cluster_center[idx, 1]), cluster_radius[idx], color='b', fill=False, lw=2)
        ax.add_artist(circle)

    if len(o_cluster_center) > 0:
        for idx in range(len(o_cluster_center)):
            circle = plt.Circle((o_cluster_center[idx, 0], o_cluster_center[idx, 1]), o_cluster_radius[idx], color='r', fill=False, lw=2)
            ax.add_artist(circle)

    plt.tight_layout()
    graph = get_graph()

    # Return
    return graph


def plot_contours (xx, yy, f, x = [], y = []):
    
    fig = plt.figure()
    plt.switch_backend('AGG')
    plt.figure(figsize=(10, 5))
    #plt.axis('off')
    contour_plot = plt.contourf(xx, yy, f, cmap='bone')

    if len(x) > 0 and len(y) > 0:
        plt.plot(x, y, ".r", markersize=6)

    plt.tight_layout()
    
    graph = get_graph()
    
    # Identify points within contours
    contours = contour_plot.collections
    del contours[0]
    
    # Return
    return contours, graph

def set_contours (data):
    
    # Extract variables from the training set
    x = np.array([float(d.dim_1) for d in data])
    y = np.array([float(d.dim_2) for d in data])

    # Selecting min and max values from the training set
    xmin, xmax = x.min(), x.max()
    ymin, ymax = y.min(), y.max()

    # Peform the kernel density estimate
    xx, yy = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
    positions = np.vstack([xx.ravel(), yy.ravel()])
    values = np.vstack([x, y])
    kernel = st.gaussian_kde(values)
    f = np.reshape(kernel(positions).T, xx.shape)
    
    # Return
    return xx, yy, f

def find_contours (x, y, contours):
    
    # Preparing an array to show results
    inside = np.full_like(x, False, dtype = bool)

    # For each level (contour), check if the data point belongs to it
    inside = []
    for c in contours:
        p = c.get_paths()[0]
        inside.append(p.contains_points(list(zip(*(x,y)))))

    # Return
    return inside

def create_cluster_model (df_train):    

    clusterer = DenStream(lambd=0.1, eps=1.5, beta=0.5, mu=3)
    y = clusterer.fit_predict(df_train[['dim_1', 'dim_2']])
    return clusterer, y

