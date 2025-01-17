from functions import *

"""
Calculate the confidence intervals for beta, where beta is acquired from
performing ordinary least-squares regression on a dataset generated by the
Franke function. Highest polynomial degree in x and y is 5.
"""
np.random.seed(10)
plt.rcParams.update({'font.size': 14})

# Define dimensions and generate dataset
n = 50
x, y, z = Franke_dataset(n, noise=0.5)
z_1d = np.ravel(z)
nx = n
ny = n

# Generate design matrix and predict using OLS
X = CreateDesignMatrix_X(x, y, 5)
beta = np.linalg.pinv(np.dot(X.T, X)) .dot(X.T) .dot(z_1d)
z_pred = X @ beta

R2 = metrics.r2_score(z_1d, z_pred)
MSE = metrics.mean_squared_error(z_1d, z_pred)

print (R2, MSE)
plot_surf(x,y,z,cm.viridis,alpha=0.25)
# plot_points(x,y,z_pred)
plt.show()

# Variance of beta
var_beta = np.diag(np.linalg.pinv(np.dot(X.T, X)) * np.var(z_1d))

# CI for beta
CI(beta, np.sqrt(var_beta), nx, ny, p=5)
