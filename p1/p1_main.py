from proj1_funcs import *
plt.rcParams.update({'font.size': 12})

"""
Perform OLS with data generated by the Franke function, without resampling.
Then find the confidence interval of beta for p = 5.
"""
# Franke_no_resampling(100)
def main(dataset='Franke',n=50,p=5,method='ols'):
    np.random.seed(15893)
    print ("Dataset:", dataset)
    print ("Method:", method)
    # Determine dataset to analyze
    if (dataset == 'Franke'):
        x, y, z = Franke_dataset(n, noise=0.5)
    else:
        z = DataImport('Norway_1arc.tif', sc=10)
        nx = len(z[0,:])
        ny = len(z[:,0])
        x = np.linspace(0,1,nx)
        y = np.linspace(0,1,ny)
        x, y = np.meshgrid(x, y)

    z_1d = np.ravel(z)

    if (dataset == 'Franke'):
        # Create design matrix, find beta, perform prediction
        X = CreateDesignMatrix_X(x, y, p)
        beta = np.linalg.pinv(np.dot(X.T, X)) .dot(X.T) .dot(z_1d)
        z_pred = X @ beta

        R2 = metrics.r2_score(z_1d, z_pred)
        MSE = metrics.mean_squared_error(z_1d, z_pred)
        # print (R2, MSE)

        # plot_surf(x,y,z,cm.viridis,alpha=0.25)
        # plot_points(x,y,z_pred)
        # plt.show()

        # Variance of beta
        var_beta = np.diag(np.linalg.pinv(np.dot(X.T, X)) * np.var(z_1d))
        # CI for beta
        # CI(beta, np.sqrt(var_beta))

    # b) and c)
    min_p = 0;  max_p = 15
    min_param = 1e-6; max_param = 1e-2
    n_params = 10

    if (method == 'ols'):
        n_params = 1   # only run once for OLS, parameter value does not matter

    polys = range(min_p,max_p)
    params = np.logspace(np.log10(min_param), np.log10(max_param), n_params)

    R2_scores,MSE_test,MSE_train,MSE_best_cv,error_test,bias_test,var_test,\
    error_train = (np.zeros((len(polys), n_params)) for i in range(8))

    for i in range(len(params)):
        for j in range(len(polys)):
            R2_scores[j,i], MSE_test[j,i], MSE_train[j,i], error_test[j,i],  bias_test[j,i], var_test[j,i], error_train[j,i] = cross_validation(x, y, z, k=5, p=polys[j], param=params[i], method=method)

    if (method == 'ols'):
        best_poly = np.argmax(MSE_test[:,0])
        best_param = 0      # just to assign a value
    else:
        min_mse_coords = np.argwhere(MSE_test==MSE_test.min())
        best_poly = polys[ min_mse_coords[0,0] ]
        best_param = params[ min_mse_coords[0,1] ]

    plot_bias_var_err(polys, bias_test, var_test, error_test, error_train)
    plot_mse_train_test(polys, MSE_test, MSE_train)

    z_, z_pred = predict_poly(x,y,z,best_poly,best_param,method)

    print ("Polynomial degree with best MSE:", best_poly)
    if (method != 'ols'):
        print ("Param with best MSE: %1.3e" % best_param)

    print ("MSE:", metrics.mean_squared_error(z_, z_pred))
    print("R2:", metrics.r2_score(z_, z_pred))


main()



# error,bias, variance plot:
# main(dataset='Franke',n=22,p=5,method='ols'), min_p = 0;  max_p = 8
# np.random.seed(15893)
