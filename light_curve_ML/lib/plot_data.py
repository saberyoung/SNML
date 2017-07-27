import matplotlib.pyplot as plt
import numpy as np
import dlt40
import itertools
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit

def func_pl(x, a, b, c, d, e):
    return e+d*x+c*x**2+b*x**3+a*x**4

def show_lc(lcdata,show):
    if not show:return
    time,mag,magerr = [],[],[]
    for ii in range(len(lcdata)):       
        time.append(float(lcdata.keys()[ii]))
        mag.append(float(lcdata.values()[ii][0]))
        try:
            magerr.append(float(lcdata.values()[ii][1]))
        except:#NULL
            pass

#    time, mag, magerr = zip(*sorted(zip(time, mag, magerr)))
    time, mag = zip(*sorted(zip(time, mag)))

    # interpolation
    fi = interp1d(time,mag, kind='nearest')
    # power law fit
    popt, pcov = curve_fit(func_pl,time,mag,maxfev=10000)
    a, b, c, d, e = popt[0], popt[1], popt[2], popt[3], popt[4]

    plt.plot(time,mag,'*')
    plt.plot(time,fi(time),'-')
    plt.plot(time,func_pl(np.array(time),a,b,c,d,e),'--')
    plt.gca().invert_yaxis()
    plt.show()

def plot_confusion_matrix(cm, classes, normalize=False, title='Confusion matrix', cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = (cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]).round(2)
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show()
