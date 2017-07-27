import matplotlib.pyplot as plt
import numpy as np
import dlt40
import itertools
from sklearn import linear_model
from matplotlib.ticker import NullFormatter

def scatter_hist(X,label1):
    plt.figure(1)
    x,y=[],[]
    dimx,dimy = X.shape
    for dim,ii,label in zip([dimx,dimy],[x,y],['x','y']):
        for xx in range(dim):            
            if label=='x':
                ii.append(sum(X[xx,:]))
            else:
                ii.append(sum(X[:,xx]))
    x,y=np.array(x),np.array(y)  

    nullfmt = NullFormatter()         # no labels

    # definitions for the axes
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left + width + 0.02

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.2]
    rect_histy = [left_h, bottom, 0.2, height]

    # start with a rectangular Figure
    plt.figure(1, figsize=(8, 8))

    axScatter = plt.axes(rect_scatter)
    axHistx = plt.axes(rect_histx)
    axHisty = plt.axes(rect_histy)

    # no labels
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)

    # the scatter plot:
    axScatter.imshow(X)
    axScatter.axis("off")

    axHistx.bar(range(dimx),x,align='center', alpha=0.5)
    axHisty.barh(range(dimy),y,align='center', alpha=0.5)

    axHistx.set_xlim(axScatter.get_xlim())
    axHisty.set_ylim(axScatter.get_ylim())

    plt.title(label1, fontsize=14, fontweight='bold')

def counts_show(X,label,cmap1,cmap2,vmin,vmax):
    plt.figure(2)
    # 1          
    sub = plt.subplot(1, 2, 1)
    sub.axis("off")
    sub.imshow(X,cmap=cmap2,interpolation="nearest",vmin=vmin, vmax=vmax)           
    # 2
    sub = plt.subplot(1, 2, 2)
    nn=0
    list1,list2 = [],[]
    for ii in X:
        for jj in ii:
            nn+=1
            list1.append(jj)
            list2.append(nn)
    sub.plot(list2,list1,'y.-')    
    plt.title(label, fontsize=14, fontweight='bold')     

def plot(X,y,show,verbose):
    vmin,vmax=0,40    
    cmap1,cmap2 = plt.cm.gray,'hot'    

    if verbose:
        # x 
        image = X[:,0]
        plt.figure(figsize=(20,10))
        plt.rcParams.update({'font.size': 10})
        plt.subplot(1, 2, 1)
        plt.hist(image.min((0,2)), bins=20, log=True)
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        plt.subplot(1, 2, 2)
        plt.hist(image.max((0,2)), bins=20, log=True);
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        plt.show()
   
        # y
        plt.hist(y, bins=np.arange(20)-0.5)
        plt.show()

    if show:    
        command = ['select id,classification from classification']
        data= dlt40.dlt40sql.query(command, dlt40.dlt40sql.conn)   
        # images
        for X,y in zip(X,y):
            X = X[0]                            
            if float(y)!=15:continue
            for ii in data:                              
                if y==ii['id']:label=ii['classification']              
            scatter_hist(X,label)
            counts_show(X,label,cmap1,cmap2,vmin,vmax)
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

def plot_error(X, y, X_train, X_test, y_train, y_test):    
    # y = np.dot(X, coef)
    coef = np.linalg.lstsq(X, y)[0]
    alphas = np.logspace(-5, 1, 60)
    enet = linear_model.ElasticNet(l1_ratio=0.8)
    train_errors = list()
    test_errors = list()
    for alpha in alphas:
        enet.set_params(alpha=alpha)
        enet.fit(X_train, y_train)
        train_errors.append(enet.score(X_train, y_train))
        test_errors.append(enet.score(X_test, y_test))

    i_alpha_optim = np.argmax(test_errors)
    alpha_optim = alphas[i_alpha_optim]
    print("Optimal regularization parameter : %s" % alpha_optim)

    # Estimate the coef_ on full data with optimal regularization parameter
    enet.set_params(alpha=alpha_optim)   
    coef_ = enet.fit(X, y).coef_
    
    plt.subplot(2, 1, 1)
    plt.semilogx(alphas, train_errors, label='Train')
    plt.semilogx(alphas, test_errors, label='Test')
    plt.vlines(alpha_optim, plt.ylim()[0], np.max(test_errors), color='k',
               linewidth=3, label='Optimum on test')
    plt.legend(loc='lower left')
#    plt.ylim([0, 1.2])
    plt.xlabel('Regularization parameter')
    plt.ylabel('Performance')

    # Show estimated coef_ vs true coef
    plt.subplot(2, 1, 2)
    plt.plot(coef_, label='True coef')
    plt.plot(coef, label='Estimated coef')
    plt.legend()
    plt.subplots_adjust(0.09, 0.04, 0.94, 0.94, 0.26, 0.26)
    plt.show()
