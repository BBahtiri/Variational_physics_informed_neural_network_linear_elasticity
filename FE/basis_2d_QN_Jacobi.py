"""
The file `basis_2d_QN_Jacobi.py` contains the class Basis2DQNJacobi which is used
to define the basis functions for a Jacobi Polynomial. Test functions and derivatives
are inferred from the work by Ehsan Kharazmi et.al (hp-VPINNs: Variational
Physics-Informed Neural Networks With Domain Decomposition) available at
https://github.com/ehsankharazmi/hp-VPINNs/

Author: Thivin Anandh D

Changelog: 30/Aug/2023 - Initial version

Known issues: None

Dependencies: scipy, numpy
"""

# import the jacobi polynomials
from scipy.special import jacobi

import numpy as np
from .basis_function_2d import BasisFunction2D


class Basis2DQNJacobi(BasisFunction2D):
    """
    This class defines the basis functions for a 2D QN element.
    """

    def __init__(self, num_shape_functions: int):
        super().__init__(num_shape_functions)

    def jacobi_wrapper(self, n, a, b, x):
        """
        Evaluate the Jacobi polynomial of degree n with parameters a and b at the given points x.

        :param n: Degree of the Jacobi polynomial.
        :type n: int
        :param a: First parameter of the Jacobi polynomial.
        :type a: float
        :param b: Second parameter of the Jacobi polynomial.
        :type b: float
        :param x: Points at which to evaluate the Jacobi polynomial.
        :type x: array_like

        :return: Values of the Jacobi polynomial at the given points x.
        :rtype: array_like
        """
        x = np.array(x, dtype=np.float64)
        return jacobi(n, a, b)(x)

    # Derivative of the Jacobi polynomials
    def djacobi(self, n, a, b, x, k: int):
        """
        Evaluate the k-th derivative of the Jacobi polynomial of degree n with parameters a and b at the given points x.

        :param n: Degree of the Jacobi polynomial.
        :type n: int
        :param a: First parameter of the Jacobi polynomial.
        :type a: float
        :param b: Second parameter of the Jacobi polynomial.
        :type b: float
        :param x: Points at which to evaluate the Jacobi polynomial.
        :type x: array_like
        :param k: Order of the derivative.
        :type k: int

        :return: Values of the k-th derivative of the Jacobi polynomial at the given points x.
        :rtype: array_like

        :raises ValueError: If the derivative order is not 1 or 2.

        :raises ImportError: If the required module 'jacobi' is not found.

        :raises Exception: If an unknown error occurs during the computation.
        """
        x = np.array(x, dtype=np.float64)
        if k == 1:
            return jacobi(n, a, b).deriv()(x)
        if k == 2:
            return jacobi(n, a, b).deriv(2)(x)
        else:
            print(f"Invalid derivative order {k} in {__name__}.")
            raise ValueError("Derivative order should be 1 or 2.")

    ## Helper Function
    def test_fcnx(self, n_test, x):
        """Compute test functions using Kharazmi's formulation."""
        test_total = []
        for n in range(1, n_test + 1):
            test = (self.jacobi_wrapper(n+1, 0, 0, x) - 
                    self.jacobi_wrapper(n-1, 0, 0, x))
            test_total.append(test)
        return np.asarray(test_total, np.float64)

    def test_fcny(self, n_test, y):
        """Compute test functions using Kharazmi's formulation."""
        test_total = []
        for n in range(1, n_test + 1):
            test = (self.jacobi_wrapper(n+1, 0, 0, y) - 
                    self.jacobi_wrapper(n-1, 0, 0, y))
            test_total.append(test)
        return np.asarray(test_total, np.float64)

    def dtest_fcn(self, n_test, x):
        """First derivatives of test functions."""
        d1test_total = []
        for n in range(1, n_test + 1):
            if n == 1:
                d1test = ((n+2)/2) * self.jacobi_wrapper(n, 1, 1, x)
            elif n == 2:
                d1test = ((n+2)/2) * self.jacobi_wrapper(n, 1, 1, x) - \
                         ((n)/2) * self.jacobi_wrapper(n-2, 1, 1, x)
            else:
                d1test = ((n+2)/2) * self.jacobi_wrapper(n, 1, 1, x) - \
                         ((n)/2) * self.jacobi_wrapper(n-2, 1, 1, x)
            d1test_total.append(d1test)
        return np.asarray(d1test_total)

    def ddtest_fcn(self, n_test, x):
        """Second derivatives of test functions."""
        d2test_total = []
        for n in range(1, n_test + 1):
            if n == 1:
                d2test = ((n+2)*(n+3)/(2*2)) * self.jacobi_wrapper(n-1, 2, 2, x)
            elif n == 2:
                d2test = ((n+2)*(n+3)/(2*2)) * self.jacobi_wrapper(n-1, 2, 2, x)
            else:
                d2test = ((n+2)*(n+3)/(2*2)) * self.jacobi_wrapper(n-1, 2, 2, x) - \
                         ((n)*(n+1)/(2*2)) * self.jacobi_wrapper(n-3, 2, 2, x)
            d2test_total.append(d2test)
        return np.asarray(d2test_total)

    def value(self, xi, eta):
        """
        This method returns the values of the basis functions at the given (xi, eta) coordinates.

        :param xi: x-coordinates at which to evaluate the basis functions.
        :type xi: array_like
        :param eta: y-coordinates at which to evaluate the basis functions.
        :type eta: array_like
        :return: Values of the basis functions.
        :rtype: array_like
        """
        num_shape_func_in_1d = int(np.sqrt(self.num_shape_functions))
        test_x = self.test_fcnx(num_shape_func_in_1d, xi)
        test_y = self.test_fcny(num_shape_func_in_1d, eta)
        values = np.zeros((self.num_shape_functions, len(xi)), dtype=np.float64)

        for i in range(num_shape_func_in_1d):
            values[num_shape_func_in_1d * i : num_shape_func_in_1d * (i + 1), :] = (
                test_x[i, :] * test_y
            )

        return values

    def gradx(self, xi, eta):
        """
        This method returns the x-derivatives of the basis functions at the given (xi, eta) coordinates.

        :param xi: x-coordinates at which to evaluate the basis functions.
        :type xi: array_like
        :param eta: y-coordinates at which to evaluate the basis functions.
        :type eta: array_like
        :return: Values of the x-derivatives of the basis functions.
        :rtype: array_like
        """
        num_shape_func_in_1d = int(np.sqrt(self.num_shape_functions))
        grad_test_x = self.dtest_fcn(num_shape_func_in_1d, xi)
        test_y = self.test_fcny(num_shape_func_in_1d, eta)
        values = np.zeros((self.num_shape_functions, len(xi)), dtype=np.float64)

        for i in range(num_shape_func_in_1d):
            values[num_shape_func_in_1d * i : num_shape_func_in_1d * (i + 1), :] = (
                grad_test_x[i, :] * test_y
            )

        return values

    def grady(self, xi, eta):
        """
        This method returns the y-derivatives of the basis functions at the given (xi, eta) coordinates.

        :param xi: x-coordinates at which to evaluate the basis functions.
        :type xi: array_like

        :param eta: y-coordinates at which to evaluate the basis functions.
        :type eta: array_like

        :return: Values of the y-derivatives of the basis functions.
        :rtype: array_like
        """
        num_shape_func_in_1d = int(np.sqrt(self.num_shape_functions))
        test_x = self.test_fcnx(num_shape_func_in_1d, xi)
        grad_test_y = self.dtest_fcn(num_shape_func_in_1d, eta)
        values = np.zeros((self.num_shape_functions, len(xi)), dtype=np.float64)

        for i in range(num_shape_func_in_1d):
            values[num_shape_func_in_1d * i : num_shape_func_in_1d * (i + 1), :] = (
                test_x[i, :] * grad_test_y
            )

        return values

    def gradxx(self, xi, eta):
        """
        This method returns the xx-derivatives of the basis functions at the given (xi, eta) coordinates.

        :param xi: x-coordinates at which to evaluate the basis functions.
        :type xi: array_like
        :param eta: y-coordinates at which to evaluate the basis functions.
        :type eta: array_like

        :return: Values of the xx-derivatives of the basis functions.
        :rtype: array_like
        """
        num_shape_func_in_1d = int(np.sqrt(self.num_shape_functions))
        grad_grad_x = self.ddtest_fcn(num_shape_func_in_1d, xi)
        test_y = self.test_fcny(num_shape_func_in_1d, eta)
        values = np.zeros((self.num_shape_functions, len(xi)), dtype=np.float64)

        for i in range(num_shape_func_in_1d):
            values[num_shape_func_in_1d * i : num_shape_func_in_1d * (i + 1), :] = (
                grad_grad_x[i, :] * test_y
            )

        return values

    def gradxy(self, xi, eta):
        """
        This method returns the xy-derivatives of the basis functions at the given (xi, eta) coordinates.

        :param xi: x-coordinates at which to evaluate the basis functions.
        :type xi: array_like
        :param eta: y-coordinates at which to evaluate the basis functions.
        :type eta: array_like
        :return: Values of the xy-derivatives of the basis functions.
        :rtype: array_like
        """
        num_shape_func_in_1d = int(np.sqrt(self.num_shape_functions))
        grad_test_x = self.dtest_fcn(num_shape_func_in_1d, xi)
        grad_test_y = self.dtest_fcn(num_shape_func_in_1d, eta)
        values = np.zeros((self.num_shape_functions, len(xi)), dtype=np.float64)

        for i in range(num_shape_func_in_1d):
            values[num_shape_func_in_1d * i : num_shape_func_in_1d * (i + 1), :] = (
                grad_test_x[i, :] * grad_test_y
            )

        return values

    def gradyy(self, xi, eta):
        """
        This method returns the yy-derivatives of the basis functions at the given (xi, eta) coordinates.

        :param xi: x-coordinates at which to evaluate the basis functions.
        :type xi: array_like
        :param eta: y-coordinates at which to evaluate the basis functions.
        :type eta: array_like

        :return: Values of the yy-derivatives of the basis functions.
        :rtype: array_like
        """
        num_shape_func_in_1d = int(np.sqrt(self.num_shape_functions))
        test_x = self.test_fcnx(num_shape_func_in_1d, xi)
        grad_grad_y = self.ddtest_fcn(num_shape_func_in_1d, eta)
        values = np.zeros((self.num_shape_functions, len(xi)), dtype=np.float64)

        for i in range(num_shape_func_in_1d):
            values[num_shape_func_in_1d * i : num_shape_func_in_1d * (i + 1), :] = (
                test_x[i, :] * grad_grad_y
            )

        return values
