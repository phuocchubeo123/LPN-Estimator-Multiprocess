from django.shortcuts import render
from django.http import HttpResponse
import home.estimator

import multiprocessing
import time
from multiprocessing import Process

cache = {}

def _calculator_with_timeout(request):
    

    keys = request.POST.copy()
    keys['csrfmiddlewaretoken']='none'

    if str(keys) in cache:
        return render(request, 'index.html', {'result': 'Load from Cache: \n' + cache[str(keys)]})

    manager = multiprocessing.Manager()
    res_dict = manager.dict()

    p = Process(target=_calculator, args=(request,res_dict))
    p.start()
    p.join(600)
    if p.is_alive():
        p.terminate()
        p.join()
        return render(request, 'index.html', {'result': "Timeout."})
    #return the output of process p
    
    if res_dict['result'] != "Please fill out all fields.":
        cache[str(keys)] = res_dict['result']

    return  render(request, 'index.html', {'result': res_dict['result']})


def calculator(request):
    try:
        return _calculator_with_timeout(request)
    except Exception as e:
        print(e)
        return render(request, 'index.html', {'result': "An error occurred."})


def _calculator(request,res_dict):
    print("Calculating...")
    print(request.POST)
    noise = request.POST.get('noise') # exact or regular
    dual = request.POST.get('dual') # on or None
    structure = request.POST.get('structure') # f2 fq or z2l
    N, n, k, t, q, l = 0, 0, 0, 0, 0, 0
    N = request.POST.get('N')
    if(dual == 'dual'):
        n = request.POST.get('n')
    k = request.POST.get('k')
    t = request.POST.get('t')
    if(structure == 'fq'):
        q = request.POST.get('q')
    if(structure == 'z2l'):
        l = request.POST.get('l')

    result = ""
    if N != None and N != "" and ((dual == 'dual' and n != None and n != "") or (dual == None and k != None and k != "")) and t != None and t != "" and ((structure == 'fq' and q != None and q != "") or (structure == 'z2l' and l != None and l != "") or structure == 'f2'):
        
        # convert to int
        N = int(N)
        if(dual == 'dual'):
            n = int(n)
        else:
            k = int(k)
        t = int(t)
        if(structure == 'fq'):
            q = int(q)
        if(structure == 'z2l'):
            l = int(l)
            
        # compute the result
        if dual == 'dual':
            if structure == 'f2':
                if noise == 'exact':
                    result = "bit security of dual exact LPN (n=" + str(n) + ", N=" + str(N) + ", t=" + str(t) + "): " + str(home.estimator.analysisfordual2(n, N, t)) + " bits"
                elif noise == 'regular':
                    result = "bit security of dual regular LPN (n=" + str(n) + ", N=" + str(N) + ", t=" + str(t) + "): "+ str(home.estimator.analysisfordual2regular(n, N, t)) + " bits"
            elif structure == 'fq':
                if noise == 'exact':
                    result = "bit security of dual exact LPN (n=" + str(n) + ", N=" + str(N) + ", t=" + str(t) + ", q=" + str(q) + "): " + str(home.estimator.analysisfordualq(n, N, t, q)) + " bits"
                elif noise == 'regular':
                    result = "bit security of regular LPN (n=" + str(n) + ", N=" + str(N) + ", t=" + str(t) + ", q=" + str(q) + "): " + str(home.estimator.analysisfordualqregular(n, N, t, q)) + " bits"
            elif structure == 'z2l':
                if noise == 'exact':
                    result = "bit security of dual exact LPN (n=" + str(n) + ", N=" + str(N) + ", t=" + str(t) + ", lambda=" + str(
                    l) + "): " + str(home.estimator.analysisfordual2lambda(n, N, t, l)) + " bits"
                elif noise == 'regular':
                    result = "bit security of dual regular LPN (n=" + str(n) + ", N=" + str(N) + ", t=" + str(t) + ", lambda=" + str(
                    l) + "): " + str(home.estimator.analysisfordual2lambdaregular(n, N, t, l)) + " bits"
        else:
            if structure == 'f2':
                if noise == 'exact':
                    print("exact LPN")
                    result = "bit security of exact LPN (N=" + str(N) + ", k=" + str(k) + ", t=" + str(t) + "): " + str(home.estimator.analysisfor2(N, k, t)) + " bits"
                elif noise == 'regular':
                    result = "bit security of regular LPN (N=" + str(N) + ", k=" + str(k) + ", t=" + str(t) + "): " + str(home.estimator.analysisfor2regular(N, k, t)) + " bits"
            elif structure == 'fq':
                if noise == 'exact':
                    result = "bit security of exact LPN (N=" + str(N) + ", k=" + str(k) + ", t=" + str(t) + ", q=" + str(q) + "): " + str(home.estimator.analysisforq(N, k, t, q)) + " bits"
                elif noise == 'regular':
                    result = "bit security of regular LPN (N=" + str(N) + ", k=" + str(k) + ", t=" + str(t) + ", q=" + str(q) + "): " + str(home.estimator.analysisforqregular(N, k, t, q)) + " bits"
            elif structure == 'z2l':
                if noise == 'exact':
                    result = "bit security of exact LPN (N=" + str(N) + ", k=" + str(k) + ", t=" + str(t) + ", lambda=" + str(l) + "): " + str(home.estimator.analysisfor2lambda(N, k, t, l)) + " bits"
                elif noise == 'regular':
                    result = "bit security of regular LPN (N=" + str(N) + ", k=" + str(k) + ", t=" + str(t) + ", lambda=" + str(l) + "): " + str(home.estimator.analysisfor2lambdaregular(N, k, t, l)) + " bits"
        res_dict['result'] = result
        return render(request, 'index.html', {'result': result})
    else:
        res_dict['result'] = "Please fill out all fields."
        return render(request, 'index.html', {'result': "Please fill out all fields."})

def contact(request):
    return render(request, 'contact.html')

def help(request):
    return render(request, 'help.html')