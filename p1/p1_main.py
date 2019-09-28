from __future__ import print_function

from proj1_funcs import *

plt.rcParams.update({'font.size': 14})

"""
Perform OLS with data generated by the Franke function, without resampling.
Then find the confidence interval of beta for p = 5.
"""
def main(n,dataset,method,p5_case=False):
    if (method not in ['ols', 'ridge', 'lasso']):
        print ('Method \"%s\" not recognized. Please use one of the following methods: ols, ridge, lasso' % method)
        sys.exit()

    # np.random.seed(6)
    np.random.seed(10)
    print ("Dataset:", dataset)
    print ("Method:", method)

    # Determine dataset to analyze
    if (dataset == 'Franke'):
        x, y, z = Franke_dataset(n, noise=0.5)
        nx = n
        ny = n
    else:
        z = DataImport('Norway_1arc.tif', sc=20)
        z = z/np.max(z)
        nx = len(z[0,:])
        ny = len(z[:,0])
        x = np.linspace(0,1,nx)
        y = np.linspace(0,1,ny)
        x, y = np.meshgrid(x, y)

    z_1d = np.ravel(z)

    # p = 5 case
    if (p5_case == True):
        # Create design matrix, find beta, perform prediction for p = 5
        # z_1d = np.ravel(FrankeFunction(x,y))
        X = CreateDesignMatrix_X(x, y, 5)
        beta = np.linalg.pinv(np.dot(X.T, X)) .dot(X.T) .dot(z_1d)
        z_pred = X @ beta

        if (dataset == 'Franke'):
            z_1d = np.ravel(FrankeFunction(x,y))

        R2 = metrics.r2_score(z_1d, z_pred)
        MSE = metrics.mean_squared_error(z_1d, z_pred)
        print (R2, MSE)
        # plot_surf(x,y,z,cm.viridis,alpha=0.25)
        # plot_points(x,y,z_pred)
        # plt.show()

        # Variance of beta
        var_beta = np.diag(np.linalg.pinv(np.dot(X.T, X)) * np.var(z_1d))
        # CI for beta
        # CI(beta, np.sqrt(var_beta), nx, ny, p=5)

    # Define ranges for complexity and parameters
    min_p = int(sys.argv[1]);  max_p = int(sys.argv[2])
    # min_param = float(sys.argv[3]); max_param = float(sys.argv[3])

    # min_param = 1e-11; max_param = 1e-9     # ridge
    min_param = 5e-6; max_param = 1e-4     # lasso
    # 5e-6 lowest param for terrain, lasso
    # 1e-5 lowest param for franke, lasso
    n_params = 5

    if (method == 'ols'):
        n_params = 1   # only run once for OLS, parameter value does not matter

    polys = np.arange(min_p,max_p)
    params = np.logspace(np.log10(min_param), np.log10(max_param), n_params)

    # Initialize arrays
    R2_scores,MSE_test,MSE_train,MSE_best_cv,error_test,bias_test,var_test,\
    error_train = (np.zeros((len(polys), n_params)) for i in range(8))
    print ("Polynomials:", polys)
    print ("Parameters:", params)

    # Perform cross-validation with given set of polynomials and parameters
    for i in range(len(params)):
        for j in range(len(polys)):
            sys.stdout.write('poly %d/%d, param %d/%d  \r' % (j+1,len(polys),i+1,len(params)))
            sys.stdout.flush()

            R2_scores[j,i], MSE_test[j,i], MSE_train[j,i], error_test[j,i],  bias_test[j,i], var_test[j,i], error_train[j,i] = cross_validation(x, y, z, k=5, p=polys[j], dataset=dataset, param=params[i], method=method)
    # end cross-validation
    print ("\n\n-----CV done-----")

    if (method == 'ols'):
        poly_ind = np.argmin(MSE_test[:,0])
        best_poly = polys[poly_ind]
        param_ind = 0

    else:
        min_mse_coords = np.argwhere(MSE_test==MSE_test.min())
        poly_ind = min_mse_coords[0,0]
        param_ind = min_mse_coords[0,1]

    best_poly = polys[ poly_ind ]
    best_param = params[ param_ind ]
    print ("Polynomial degree with best MSE:", best_poly)
    print ("Param with best MSE: %1.3e" % best_param)
    print ("MSE:", MSE_test[poly_ind, param_ind])
    print("R2:", R2_scores[poly_ind, param_ind])

    # plot_bias_var_err(polys, bias_test, var_test, error_test, error_train)
    plot_mse_train_test(polys, MSE_test, MSE_train, params, nx, ny)
    plot_mse_poly_param(params, polys, MSE_test)

    # Compare with true data if using Franke dataset
    if (dataset == 'Franke'):
        z = FrankeFunction(x,y)

    # perform prediction for given polynomial degree, hyperparameter
    # z_, z_pred = predict_poly(x,y,z,37,0,method)
    #
    # z_pred_2d = np.reshape(z_pred, (ny,nx))
    # plot_surf(x,y,z,color=cm.coolwarm, alpha=0.25)
    # plot_pred(x,y,z_pred_2d)
    # plt.show()

main(n=50,dataset='Terrain',method=sys.argv[3],p5_case=False)


# mse_train vs mse_test plot:
# np.random.seed(6)
# noise = 0.5
# main(dataset='Franke',n=50,method='ols'), min_p = 0;  max_p = 15

# mse_train vs mse_test plot (ridge):
# np.random.seed(10)
# noise = 0.65
# main(dataset='Franke',n=50,method='ridge'), min_p = 0;  max_p = 15

# OLS: [30, 35]
# Polynomial degree with best MSE: 32
# MSE: 0.008709927121078737
# R2: 0.6834769846192777

"""BEST OLS"""
# OLS [35, 40]
# Polynomial degree with best MSE: 37
# MSE: 0.008571487664039664
# R2: 0.6886234877217973
""""""
# OLS [55, 60]
# Polynomial degree with best MSE: 58
# MSE: 0.009294122238973608
# R2: 0.6590335437080858

# ridge [20, 60]
# Polynomial degree with best MSE: 50
# Param with best MSE: 1.000e-10
# MSE: 0.00826236034127675
# R2: 0.6988507414623765
"""BEST RIDGE"""
# ridge [60, 70]
# Polynomial degree with best MSE: 66
# Param with best MSE: 1.000e-10
# MSE: 0.008169589154065321
# R2: 0.7049167780530339
""""""

# ridge [70, 75]
# Polynomial degree with best MSE: 72
# Param with best MSE: 1.000e-10
# MSE: 0.00858005532535686
# R2: 0.6932725564380111

# ridge [60, 70]
# Polynomial degree with best MSE: 67
# Param with best MSE: 1.000e-10
# MSE: 0.008254560123138986
# R2: 0.7022500986215595

# lasso [60, 70]
# Polynomial degree with best MSE: 64
# Param with best MSE: 1.000e-04
# MSE: 0.013852126084183047
# R2: 0.5008935864756843

# lasso [60, 70]
# Polynomial degree with best MSE: 64
# Param with best MSE: 5.000e-06
# MSE: 0.012571913670866472
# R2: 0.5467698141388012
