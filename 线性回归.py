import numpy as np
form numpy import genfromtxt
import mpl_toolkits.mplot3d import Axes3D

data =genfromtxt(r"",delimiter=',')
print(data)

x_data=data[:,:-1]
y_data=data[:,-1]

print(x_data)
print(y_data)

lr=0.0001
theta0=0
theta1=0
theta2=0

epochs=1000


def compute_error(theta0,theta1,theta2,x_data,y_data):
    totalError=0
    for i in range(0,len(x_data)):
        totalError+=(y_data[i]-(theta1*x_data[i,0]+theta2*x_data[i,1]+theta0))**2
    return totalError/len(x_data)

# def gradient_descent_runner(x_date,)