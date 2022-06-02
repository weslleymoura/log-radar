from email import charset
from tracemalloc import is_tracing
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.conf import Settings, settings
from django.core.mail import send_mail
import pandas as pd
import numpy as np
from .train import plot_clusters, set_contours, plot_contours, find_contours, create_cluster_model
from .models import DataPoint
from .forms import DataPointForm
from django.core.paginator import Paginator
import pickle
import os
from django.views.decorators.csrf import csrf_exempt
import requests
import json

def home (request):

    # Template name
    template_name = 'core/home.html'

    # Context
    context = {}

    # Return
    return render (request, template_name, context)

def route (request, origin = None, destination = None):

    # Retrieving parameters
    if not origin and not destination:
        origin = request.GET.get('origin', '')
        destination =  request.GET.get('destination', '')

    # Template name
    template_name = 'core/route.html'

    # Context
    context = {}
    context['origin'] = origin
    context['destination'] = destination

    # Check parameters
    if origin == '' or destination == '':
        messages.warning(request, 'Please, you must type an origin and a destination.')
        return render (request, template_name, context)

    # Try to load contours
    try:

        # load xx
        filename = 'artefacts/xx_{}_{}.npy'.format(origin, destination)
        xx = np.load(filename, allow_pickle=True)

        # load yy
        filename = 'artefacts/yy_{}_{}.npy'.format(origin, destination)
        yy = np.load(filename, allow_pickle=True)

        # load f
        filename = 'artefacts/f_{}_{}.npy'.format(origin, destination)
        f = np.load(filename, allow_pickle=True)

        # load cluster model
        filename = 'artefacts/cluster_{}_{}'.format(origin, destination)
        clusterer = pickle.load(open(filename, 'rb'))

        # Message
        messages.success(request, 'Contours ware successfully loaded.')
    
    # Else, create contours
    except:

        # Fetch train data points
        data =  DataPoint.objects.filter(origin = origin, destination = destination, is_active = True, is_train = True)

        # Convert Queryset to Dataframe
        d = data.values()
        df_data = pd.DataFrame.from_records(d)
        
        # Check data load
        if len(data) == 0:
            messages.error(request, 'Error! There is no data to train a model for this origin and destination.')
            return HttpResponseRedirect(request.path_info)

        # Setting up contours
        xx, yy, f = set_contours (data)

        # Setting up a cluster model
        clusterer, y = create_cluster_model(df_data)

        # dump xx
        filename = 'artefacts/xx_{}_{}'.format(origin, destination)
        np.save(filename, xx, allow_pickle=True)

        # dump yy
        filename = 'artefacts/yy_{}_{}'.format(origin, destination)
        np.save(filename, yy, allow_pickle=True)

        # dump f
        filename = 'artefacts/f_{}_{}'.format(origin, destination)
        np.save(filename, f, allow_pickle=True)

        # dump cluster model
        filename = 'artefacts/cluster_{}_{}'.format(origin, destination)
        pickle.dump(clusterer, open(filename, 'wb'))

        # dump micro cluster weights
        new_micro_cluster_weights = [c.sum_of_weights for c in clusterer.p_micro_clusters]
        new_micro_cluster_weights_perc = [i/sum(new_micro_cluster_weights) for i in new_micro_cluster_weights]
        filename = 'artefacts/micro_cluster_weights_{}_{}.npy'.format(origin, destination)
        np.save(filename, new_micro_cluster_weights_perc, allow_pickle=True)

        # Message
        messages.success(request, 'Contours ware successfully created.')
    
    # Fetch current datapoints (just to show non-training points)
    data =  DataPoint.objects.filter(origin = origin, destination = destination, is_active = True, is_train = False)
    x = np.array([float(d.dim_1) for d in data])
    y = np.array([float(d.dim_2) for d in data])
    total = len(data)

    # Contourf plot
    contours, chart = plot_contours (xx = xx, yy = yy, f = f, x = x, y = y)

    # Cluster plot
    chart_cluster = plot_clusters (clusterer)

    # Check the number of contours for each data point
    n_risk = 0
    n_regular = 0
    if total > 0:

        # Find contours
        inside = find_contours (x = x, y = y, contours = contours)

        # Convert Queryset to Dataframe
        d = data.values()
        data = pd.DataFrame.from_records(d)

        # Enrich the training set with results
        data['n_contours'] = sum(inside)

        # Show data points which are far from the densest points
        n_risk = len(data.loc[data['n_contours'] == 0, ])
        n_regular = total - n_risk

    # Context
    context['chart'] = chart
    context['chart_cluster'] = chart_cluster
    context['n_risk'] = n_risk
    context['n_regular'] = n_regular

    # Return
    return render (request, template_name, context)

def update_system_after_new_data_point (origin, destination, dim_1, dim_2):

    # Prepare returning message
    msg = ''

    # load cluster model
    filename = 'artefacts/cluster_{}_{}'.format(origin, destination)
    clusterer = pickle.load(open(filename, 'rb'))

    # load micro cluster weights
    filename = 'artefacts/micro_cluster_weights_{}_{}.npy'.format(origin, destination)
    current_micro_cluster_weights_perc = np.load(filename, allow_pickle=True)

    # Perform the partial fit
    clusterer.partial_fit([[dim_1, dim_2]], 1)

    # Check the new state
    new_current_p_micro_clusters = len(clusterer.p_micro_clusters)
    new_current_o_micro_clusters = len(clusterer.o_micro_clusters)

    # Check micro cluster weights
    new_micro_cluster_weights = [c.sum_of_weights for c in clusterer.p_micro_clusters]
    new_micro_cluster_weights_perc = [i/sum(new_micro_cluster_weights) for i in new_micro_cluster_weights]

    print(current_micro_cluster_weights_perc)
    print(new_micro_cluster_weights_perc)

    # Check if the data has changed 
    has_changed = False
    for i in range(0, len(current_micro_cluster_weights_perc)):
        diff = abs(current_micro_cluster_weights_perc[i] - new_micro_cluster_weights_perc[i])
        if diff >= 0.001:
            has_changed = True
            break

    print('Mudou?')
    print(has_changed)

    if has_changed:
    
        # Select data
        data =  DataPoint.objects.filter(origin = origin, destination = destination, is_active = True)

        # Convert Queryset to Dataframe
        d = data.values()
        df_data = pd.DataFrame.from_records(d)

        # Recreate clusters
        clusterer, y = create_cluster_model(df_data)
        
        # Recreate contours
        xx, yy, f = set_contours (data)

        # dump xx
        filename = 'artefacts/xx_{}_{}'.format(origin, destination)
        np.save(filename, xx, allow_pickle=True)

        # dump yy
        filename = 'artefacts/yy_{}_{}'.format(origin, destination)
        np.save(filename, yy, allow_pickle=True)

        # dump f
        filename = 'artefacts/f_{}_{}'.format(origin, destination)
        np.save(filename, f, allow_pickle=True)

        # dump micro cluster weights
        new_micro_cluster_weights = [c.sum_of_weights for c in clusterer.p_micro_clusters]
        new_micro_cluster_weights_perc = [i/sum(new_micro_cluster_weights) for i in new_micro_cluster_weights]
        filename = 'artefacts/micro_cluster_weights_{}_{}.npy'.format(origin, destination)
        np.save(filename, new_micro_cluster_weights_perc, allow_pickle=True)

        filename = 'artefacts/micro_cluster_weights_{}_{}.npy'.format(origin, destination)

        # Logging
        msg = 'The cluster model and contours have been retrained with the new data'

    # dump cluster model
    filename = 'artefacts/cluster_{}_{}'.format(origin, destination)
    pickle.dump(clusterer, open(filename, 'wb'))

    # Return
    return msg

def add_data_point (request, origin = None, destination = None):

    template_name = 'core/add_data_point.html'
    context = {}
    if request.method == 'POST':

        # Receiving post arguments
        dim_1 = request.POST.get('dim_1', None)
        dim_2 = request.POST.get('dim_2', None)
        business_key = request.POST.get('business_key', None)
        origin = request.POST.get('origin', None)
        destination = request.POST.get('destination', None)

        form = DataPointForm(request.POST)
        if form.is_valid():

            # Save the new data point
            form.save()
            messages.success(request, 'The new data point was successfully created.')

            msg = update_system_after_new_data_point (origin, destination, dim_1, dim_2)
            if msg != '':
                messages.success(request, msg)

            return redirect('core:route', origin, destination)

    # Load form
    form = DataPointForm()
    context['form'] = form
    context['origin'] = origin
    context['destination'] = destination
    return render(request, template_name, context)

def reset_data_points(request):

    # Removing all data points
    DataPoint.objects.all().delete()

    # Reading the training set
    df_train = pd.read_csv("data/train.csv")
    
    # Inserting data into the database
    for index, row in df_train.iterrows():

        # Instantiating a new train data point object
        data_point = DataPoint()
        data_point.is_train = True

        # Adding dimensions
        try:
            data_point.dim_1 = row['x']
            data_point.dim_2 = row['y']
        except:
            messages.error(request, 'Error! Columns "x" and "y" are mandatory, please review the file')
            return redirect('core:home')

        # Adding origin and destination
        try:
            data_point.origin = row['origin']
            data_point.destination = row['destination']
        except:
            data_point.origin = 'DEFAULT ORIGIN'
            data_point.destination = 'DEFAULT DESTINATION'

        # Adding business key
        try:
            data_point.business_key = row['business_key']
        except:
            pass

        # Saving the new data point
        data_point.save()
    
    # Removing current models
    dir = 'artefacts'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))

    # Return
    messages.success(request, 'Data points have been successfully imported')
    return redirect('core:home')

def list_data_points(request, origin = None, destination = None, type = None):

    # Template name
    template_name = 'core/list_data_points.html'

    # Fetch data points
    data_points = DataPoint.objects.filter(origin = origin, destination = destination, is_active = True)
    x = np.array([float(d.dim_1) for d in data_points])
    y = np.array([float(d.dim_2) for d in data_points])

    # load xx
    filename = 'artefacts/xx_{}_{}.npy'.format(origin, destination)
    xx = np.load(filename, allow_pickle=True)

    # load yy
    filename = 'artefacts/yy_{}_{}.npy'.format(origin, destination)
    yy = np.load(filename, allow_pickle=True)

    # load f
    filename = 'artefacts/f_{}_{}.npy'.format(origin, destination)
    f = np.load(filename, allow_pickle=True)

    # Contourf plot
    contours, chart = plot_contours (xx = xx, yy = yy, f = f)

    # Classify data points
    inside = find_contours (x = x, y = y, contours = contours)
    inside =  sum(inside)
    
    # Enrich the training set with results
    i = 0
    while i < len(inside):
        data_points[i].n_contours = inside[i]
        i += 1

    # Filter data points
    if type == 'flagged':
        data_points = [d for d in data_points if d.is_train == False and d.n_contours == 0]
    elif type == 'regular':
        data_points = [d for d in data_points if d.is_train == False and d.n_contours > 0]
    else:
        data_points = [d for d in data_points if d.is_train]

    # Paginate
    page_number = request.GET.get('page', 1)
    paginator = Paginator(data_points, 10)
    page_obj = paginator.get_page(page_number)

    context = {
        'data_points': page_obj,
        'origin': origin,
        'destination': destination
    }
    return render (request, template_name, context)


@csrf_exempt
def process_sns_message (request):
    body = json.loads(request.body)
    print(body)

    # Confirm topic subscription
    if request.headers['x-amz-sns-message-type'] == 'SubscriptionConfirmation':
        x = requests.get(body['SubscribeURL'])

    # Else process the message
    elif request.headers['x-amz-sns-message-type'] == 'Notification':
        
        # Reading the message
        msg = body['Message']
        print('The message is: {}'.format(msg))

        # Convert string to dict
        msg = eval(msg)

        # Receiving post arguments
        dim_1 = msg['dim_1']
        dim_2 = msg['dim_2']
        business_key = msg['business_key']
        origin = msg['origin']
        destination = msg['destination']

        # Save
        data_point = DataPoint()
        data_point.dim_1 = dim_1
        data_point.dim_2 = dim_2
        data_point.business_key = business_key
        data_point.origin = origin
        data_point.destination = destination
        data_point.save()

        # Insert the new data poiont
        msg = update_system_after_new_data_point (origin, destination, dim_1, dim_2)

    else:
        print('The system cannot recognize x-amz-sns-message-type: {}'.format(request.headers['x-amz-sns-message-type']))

    return HttpResponse('ok')

def add_user (request):
    pass

def user_login(request):
    pass

