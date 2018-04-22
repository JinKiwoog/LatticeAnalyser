import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
import types

class LineFit:
	"""
	Line fit based on article by Lavagini et al (2007).
	"""
	def __init__(self, x, y, y_err=None):
		assert len(x) == len(y), "array lengths to not match"
		self.x = x
		self.y = y
		self.y_err = y_err
		self.n = len(y)
		self.x_lower = np.min(self.x)
		self.x_upper = np.max(self.x)

		# Sets weigths regardless if they are to be used or not.
		self.w = self._get_weights(self.y_err)

		self.inverse_fit_performed = False

	def fit(self, x_arr=None):
		"""
		Fits a linear function,
			y_hat = b0 + b1 * x
		from a provided dataset, x, y and y_err from initialization.

		Args:
			x_arr: optional array for which return as a fit. Default is None.

		Returns:
			y_hat: returns fit(x)
			y_hat_err: returns fit_error(x)
			fit_params: list containing b0, b0_err, b1, b1_err
			chi_squared: goodness of fit
		"""

		if isinstance(x_arr, types.NoneType):
			x_arr = np.linspace(self.x[self.x_lower], self.x[self.x_upper], 100)

		# self.x_mean = np.mean(self.x)
		# self.y_mean = np.mean(self.y)

		# # Temporary sum contained in both eq. 4, eq. 6 and eq. 7
		# self.xi_xmean_sum = np.sum((self.x - self.x_mean)**2)
		
		self.x_mean, self.y_mean, self.xi_xmean_sum = self._get_means()

		# Eq. 5
		self.s_xy_err = self._get_s_xy()
		# self.s_xy_err = np.sum((self.y - self._y_hat(self.x))**2) / (self.n - 2)

		# Eq. 4
		self.b1 = np.sum((self.x - self.x_mean) * self.y) / self.xi_xmean_sum

		# Eq. 3
		self.b0 = self.y_mean - self.b1 * self.x_mean

		# Eq. 6
		self.b0_err = self.s_xy_err
		self.b0_err *= (1.0 / self.n + self.x_mean ** 2 / self.xi_xmean_sum)

		# Eq. 7
		self.b1_err = self.s_xy_err / self.xi_xmean_sum

		fit_params = [self.b0, self.b0_err, self.b1, self.b1_err]

		# Goodness of fit
		self.chi = self._chi_squared(self.y, self.y_err, self._y_hat(self.x))

		self.x_fit = x_arr
		self.y_fit = self._y_hat(x_arr)
		self.y_fit_err = self._y_hat_err(x_arr)

		return self.y_fit, self.y_fit_err, fit_params, self.chi

	def _y_hat(self, x):		
		"""Unweigthed y(x), eq. 1."""
		return self.b0 + self.b1 * x

	def _y_hat_err(self, x):
		"""Unweigthed y(x) error, eq. 8b."""
		_pt1 = self.b0 + self.b1 * x
		_pt2 = scipy.stats.t.isf(0.32, self.n - 2) * np.sqrt(self.s_xy_err) 
		_pt2 *= np.sqrt(1.0 / self.n + (x - self.x_mean)**2 / self.xi_xmean_sum)
		return [_pt1 - _pt2, _pt1 + _pt2]

	def fit_weighted(self, x_arr=None):
		"""
		Performs a weighted fit based on x, y, and y_err provided in 
		initialization.

		Args:
			x_arr: optional array for which return as a fit. Default is None.

		Returns:
			y_hat: returns fit(x)
			y_hat_err: returns fit_error(x)
			fit_params: list containing b0, b0_err, b1, b1_err
			chi_squared: goodness of fit
		"""

		if isinstance(x_arr, types.NoneType):
			x_arr = np.linspace(self.x[0], self.x[-1], 100)

		assert not isinstance(self.y_err, types.NoneType), "Missing y_err."

		# self.xw_mean = np.sum(self.w * self.x) / np.sum(self.w)
		# self.yw_mean = np.sum(self.w * self.y) / np.sum(self.w)

		# # Temporary som contained in both eq. 4, eq. 6 and eq. 7
		# self.xwi_xmean_sum = np.sum(self.w * (self.x - self.xw_mean)**2)
		self.xw_mean, self.yw_mean, self.xwi_xmean_sum = self._get_means_weigthed()

		# # Eq. 21
		# self.s_xyw_err = np.sum(self.w * (self.y - self._yw_hat(self.x))**2)
		# self.s_xyw_err /= (self.n - 2.0) 

		self.s_xyw_err = self._get_s_xyw()

		# Eq. 18
		self.b1w = np.sum(self.w * (self.x - self.xw_mean) * self.y)
		self.b1w /= self.xwi_xmean_sum

		# Eq. 17
		self.b0w = self.yw_mean - self.b1w * self.xw_mean

		# Eq. 19
		self.b0w_err = (1.0/np.sum(self.w) + self.xw_mean**2 / self.xwi_xmean_sum) 
		self.b0w_err *= self.s_xyw_err

		# Eq. 20
		self.b1w_err = self.s_xyw_err / self.xwi_xmean_sum

		fit_params = [self.b0w, self.b0w_err, self.b1w, self.b1w_err]

		# Goodness of fit
		self.chi_w = self._chi_squared(self.y, self.y_err, self._yw_hat(self.x))

		# Stores variables for later possible use
		self.xw_fit = x_arr
		self.yw_fit = self._yw_hat(x_arr)
		self.yw_fit_err = self._yw_hat_err(x_arr)

		return self.yw_fit, self.yw_fit_err, fit_params, self.chi_w

	def _yw_hat(self, x):
		"""weigthed y(x), eq. 1"""
		return self.b0w + self.b1w * x

	def _yw_hat_err(self, x):
		"""Weigthed y(x) errors, eq. 22."""
		_pt1 = self.b0w + self.b1w * x
		_pt2 = scipy.stats.t.isf(0.32, self.n - 2) * np.sqrt(self.s_xyw_err) 
		_pt2 *= np.sqrt(1.0 / np.sum(self.w) + (x - self.xw_mean)**2 / self.xwi_xmean_sum)

		# print [_pt1 - _pt2, _pt1 + _pt2]

		return [_pt1 - _pt2, _pt1 + _pt2]

	def _get_s_xy(self):
		"""Eq. 5."""
		return np.sum((self.y - self._y_hat(self.x))**2) / (self.n - 2)

	def _get_s_xyw(self):
		"""Eq. 21."""
		s_xyw_err = np.sum(self.w * (self.y - self._yw_hat(self.x))**2)
		return s_xyw_err/(self.n - 2.0)

	def _get_means(self):
		""" Returns non-weigthed means."""
		# Eq. 4, eq. 6 and eq. 7
		x_mean = np.mean(self.x)
		xi_xmean_sum = np.sum((self.x - x_mean)**2)
		return x_mean, np.mean(self.y), xi_xmean_sum

	def _get_means_weigthed(self):
		"""Sets weighted means."""
		xw_mean = np.sum(self.w * self.x) / np.sum(self.w)
		yw_mean = np.sum(self.w * self.y) / np.sum(self.w)

		# Temporary som contained in both eq. 4, eq. 6 and eq. 7
		xwi_xmean_sum = np.sum(self.w * (self.x - xw_mean)**2)
		return xw_mean, yw_mean, xwi_xmean_sum

	def _get_weights(self, y_err):
		"""Sets weights based on error in fit."""
		return 1.0/y_err**2

	def set_fit_parameters(self, b0, b0_err, b1, b1_err, weighted=False):
		"""
		Method for setting fit parameters if they have been retrieved by 
		another method, such as scipy.optimize.curve_fit.

		Args:
			b0: constant term in line fit.
			b0: error of constant term in line fit.
			b1: slope term in line fit.
			b1: error of slope term in line fit.
		"""
		if weighted:
			self.b0w = b0
			self.b0w_err = b0_err
			self.b1w = b1
			self.b1w_err = b1_err
			self.xw_mean, self.yw_mean, self.xwi_xmean_sum \
				= self._get_means_weigthed()
			self.s_xyw_err = self._get_s_xyw()
		else:
			self.b0 = b0
			self.b0_err = b0_err
			self.b1 = b1
			self.b1_err = b1_err

			self.x_mean, self.y_mean, self.xi_xmean_sum \
				= self._get_means()
			self.s_xy_err = self._get_s_xy()

	def __call__(self, x, weighted=False):
		"""Returns the fitted function at x."""
		if weighted:
			y_fit, y_fit_err = self._yw_hat(x), self._yw_hat_err(x)
			return y_fit, y_fit_err, self._chi_squared(self.y, self.y_err, 
				self._yw_hat(self.x))
		else:
			y_fit, y_fit_err = self._y_hat(x), self._y_hat_err(x)
			return y_fit, y_fit_err, self._chi_squared(self.y, self.y_err, 
				self._y_hat(self.x))


	def inverse_fit(self, y0, weigthed=False):
		"""
		Inverse fiting on the values we have performed a fit one.

		Args:
			y0: target fit at y-axis, float.
			weigthed: bool, if we are to use weighted fit or not.

		Returns:
			x0: targeted y0 fit
			x0_err: errorband at y0 fit
		"""
		n = 100000
		x = np.linspace(self.x_lower, self.x_upper, n)

		if weigthed:
			# Finds the target value
			x0_index = np.argmin(np.abs(y0 - self._yw_hat(x)))
			x0 = x[x0_index]

			# Finds the error bands
			x_err_neg, x_err_pos = self._yw_hat_err(x)
			x0_err_index_neg = np.argmin(np.abs(y0 - x_err_pos))
			x0_err_index_pos = np.argmin(np.abs(y0 - x_err_neg))
			x0_err = [x[x0_err_index_neg], x[x0_err_index_pos]]

		else:
			# Finds the target value
			min_index = np.argmin(np.abs(y0 - self._y_hat(x)))
			x0 = x[min_index]

			# Finds the error bands
			x_err_neg, x_err_pos = self._y_hat_err(x)
			x0_err_index_neg = np.argmin(np.abs(y0 - x_err_pos))
			x0_err_index_pos = np.argmin(np.abs(y0 - x_err_neg))
			x0_err = [x[x0_err_index_neg], x[x0_err_index_pos]]

		self.y0 = y0
		self.x0 = x0
		self.x0_err = x0_err

		self.inverse_fit_performed = True

		return x0, x0_err

	def _chi_squared(self, y, y_err, y_fit):
		"""Goodness test of fit."""
		return np.sum((y - y_fit)**2 / y_err**2) / (self.n - 2.0)

	def plot(self, weighted=False):
		"""Use full function for quickly checking the fit."""

		# Gets the line fitted and its errors
		if self.inverse_fit_performed:
			fit_target = self.y0
			x_fit = self.x0
			x_fit_err = self.x0_err

		# Gets the signal
		x = self.x
		signal = self.y
		signal_err = self.y_err

		# Gets the fitted line
		if weighted:
			x_hat = self.xw_fit
			y_hat = self.yw_fit
			y_hat_err = self.yw_fit_err
			chi = self.chi_w
			fit_label = "Weigthed fit"
			fit_target_label = r"$x_{0,w}\pm\sigma_{x_0,w}$"
		else:
			x_hat = self.x_fit
			y_hat = self.y_fit
			y_hat_err = self.y_fit_err
			chi = self.chi
			fit_label = "Unweigthed fit"
			fit_target_label = r"$x_0\pm\sigma_{x_0}$"

		fig1 = plt.figure()
		ax1 = fig1.add_subplot(111)
		ax1.plot(x_hat, y_hat, label=fit_label, color="tab:blue")
		ax1.fill_between(x_hat, y_hat_err[0], y_hat_err[1], alpha=0.5, 
			color="tab:blue")
		ax1.errorbar(x, signal, yerr=signal_err, marker="o", label="Signal", 
			linestyle="none", color="tab:orange")
		title_string = r"$\chi^2 = %.2f" % chi 

		if self.inverse_fit_performed:
			ax1.axhline(fit_target, linestyle="dashed", color="tab:grey")
			ax1.axvline(x_fit, color="tab:orange")
			ax1.fill_betweenx(np.linspace(np.min(y_hat),np.max(y_hat),100),
				x_fit_err[0], x_fit_err[1], label=fit_target_label, alpha=0.5, 
				color="tab:orange")
			title_string += r", x_0 = %.2f \pm%.2f$" % (x_fit,
			(x_fit_err[1] - x_fit_err[0]) / 2.0)

		ax1.legend(loc="best", prop={"size":8})
		ax1.set_title(title_string)
		plt.show()
		plt.close(fig1)

def _fit_var_printer(var_name, var, var_error, w=16):
	return "{0:<s} = {1:<.{w}f} +/- {2:<.{w}f}".format(var_name, var, 
		var_error, w=w)


def _test_simple_line_fit():
	"""
	Function for testing the case where one compares the curve_fit module in
	scipy.optimize with what I have created.

	SciPy and LineFit should fit exact down to around 8th digit.
	"""
	import random
	import scipy.optimize as sciopt

	# Generates signal with noise
	a = 0.65
	b = 1.1
	N = 10
	x = np.linspace(0, 5, N)
	signal_spread = 0.5
	signal = a*x + b + np.random.uniform(-signal_spread, signal_spread, N)
	signal_err = np.random.uniform(0.1, 0.3, N)

	fit = LineFit(x, signal, signal_err)
	x_hat = np.linspace(0, 5, 100)

	# Unweigthed fit
	y_hat, y_hat_err, f_params, chi_unweigthed = fit.fit(x_hat)
	b0, b0_err, b1, b1_err = f_params

	# Fits without any weights first
	pol1, polcov1 = sciopt.curve_fit(lambda x, a, b : x*a + b, x, signal)

	# Fit target
	fit_target = 2.5
	x_fit, x_fit_err = fit.inverse_fit(fit_target)

	# Numpy polyfit
	# polyfit1, polyfitcov1 = np.polyfit(x, signal, 1, cov=True)
	# polyfit_err = np.sqrt(np.diag(polyfitcov1))
	polyfit1, polyfitcov1 = np.polyfit(x, signal, 1, cov=True)
	polyfit_err = np.sqrt(np.diag(polyfitcov1))

	print "UNWEIGTHED LINE FIT"
	print "Numpy polyfit:"
	print _fit_var_printer("a", polyfit1[0], polyfit_err[0])
	print _fit_var_printer("b", polyfit1[1], polyfit_err[1])

	print "SciPy curve_fit:"
	print _fit_var_printer("a", pol1[0], polcov1[0,0])
	print _fit_var_printer("b", pol1[1], polcov1[1,1])

	print "LineFit:"
	print _fit_var_printer("a", b1, b1_err)
	print _fit_var_printer("b", b0, b0_err)
	print "Goodness of fit: %f" % chi_unweigthed
	# print "b = {0:<.10f} +/- {1:<.10f}".format(b0, self.b0_err)

	fig1 = plt.figure()
	ax1 = fig1.add_subplot(211)
	ax1.axhline(fit_target, linestyle="dashed", color="tab:grey")
	ax1.plot(x_hat, y_hat, label="Unweigthed fit", color="tab:blue")
	ax1.fill_between(x_hat, y_hat_err[0], y_hat_err[1], alpha=0.5, color="tab:blue")
	ax1.errorbar(x, signal, yerr=signal_err, marker="o", label="Signal", linestyle="none", color="tab:orange")
	ax1.set_ylim(0.5, 5)
	ax1.axvline(x_fit, color="tab:orange")
	ax1.fill_betweenx(np.linspace(0,6,100), x_fit_err[0], x_fit_err[1], label=r"$x_0\pm\sigma_{x_0}$", alpha=0.5, color="tab:orange")
	ax1.legend(loc="best", prop={"size":8})
	ax1.set_title("Fit test - unweigthed")

	# Weighted curve_fit
	print "WEIGTHED LINE FIT"

	# Numpy polyfit
	polyfit1, polyfitcov1 = np.polyfit(x, signal, 1, cov=True, w=1/signal_err)
	polyfit_err = np.sqrt(np.diag(polyfitcov1))
	print "Numpy polyfit:"
	print _fit_var_printer("a", polyfit1[0], polyfit_err[0])
	print _fit_var_printer("b", polyfit1[1], polyfit_err[1])

	# SciPy curve fit
	polw, polcovw = sciopt.curve_fit(lambda x, a, b : x*a + b, x, signal, sigma=signal_err)
	print "SciPy curve_fit:"
	print _fit_var_printer("a", polw[0], polcovw[0,0])
	print _fit_var_printer("b", polw[1], polcovw[1,1])

	# Weighted LineFit
	yw_hat, yw_hat_err, f_params_weigthed, chi_weigthed = fit.fit_weighted(x_hat)
	b0, b0_err, b1, b1_err = f_params_weigthed
	xw_fit, xw_fit_error = fit.inverse_fit(fit_target, weigthed=True)

	print "LineFit:"
	print _fit_var_printer("a", b1, b1_err)
	print _fit_var_printer("b", b0, b0_err)
	print "Goodness of fit: %f" % chi_weigthed

	ax2 = fig1.add_subplot(212)
	ax2.axhline(fit_target, linestyle="dashed", color="tab:grey")
	ax2.errorbar(x, signal, yerr=signal_err, marker="o", label="Signal", linestyle="none", color="tab:orange")
	ax2.plot(x_hat, yw_hat, label="Weighted fit", color="tab:blue")
	ax2.fill_between(x_hat, yw_hat_err[0], yw_hat_err[1], alpha=0.5, color="tab:blue")
	ax2.set_ylim(0.5, 5)
	ax2.axvline(xw_fit, color="tab:orange")
	ax2.fill_betweenx(np.linspace(0,6,100), xw_fit_error[0], xw_fit_error[1], label=r"$x_{0,w}\pm\sigma_{x_0,w}$", alpha=0.5, color="tab:orange")
	ax2.legend(loc="best", prop={"size":8})
	plt.show()

	# fit.plot(True)

def _test_inverse_line_fit():
	"""
	Function for testing the inverse line fit.
	"""
	import random
	import scipy.optimize as sciopt

	# Generates signal with noise
	x_start = 0
	x_end = 5
	a = 0.65
	b = 1.1
	N = 50
	M = 10 # Number of data points at each point
	x = np.linspace(x_start, x_end, N)
	x_matrix = (np.ones((M, N)) * x)
	signal_spread = 0.5
	signal = np.random.uniform(-signal_spread, signal_spread, (M, N)) + a*x_matrix + b
	signal_err = np.std(signal, axis=0)
	signal_mean = np.mean(signal, axis=0)
	# signal = a*x + b + np.random.uniform(-signal_spread, signal_spread, N)
	# signal_err = np.random.uniform(0.1, 0.3, N)

	# My line fit
	x_hat = np.linspace(x_start, x_end, 100)

	print signal.shape, x.shape, x_matrix.shape, np.cov(signal.T).shape

	def _f(_x, a, b):
		# print (_x*a + b).shape
		return _x*a + b

	print sciopt.least_squares.__doc__
	# Unweigthed fit
	# pol1, polcov1 = sciopt.curve_fit(_f, x, signal_mean, sigma=signal_err)
	pol1, polcov1 = sciopt.curve_fit(_f, x, signal_mean, sigma=np.cov(signal.T))


	# pol1, polcov1 = np.polyfit(x, signal.T, 1, cov=True)
	# print pol1.shape
	# print polcov1.shape

	# fit_par = np.mean(pol1, axis=1)
	# fit_cov = np.mean(polcov1, axis=2)
	fit_par = pol1
	fit_cov = polcov1

	# print np.cov(signal_mean.T)
	lfit = LineFit(x, signal_mean, signal_err)
	# lfit.set_fit_parameters(pol1[1], np.sqrt(polcov1[1,1]), pol1[0], np.sqrt(polcov1[0,0]), weighted=True)
	lfit.set_fit_parameters(fit_par[1], np.sqrt(fit_cov[1,1]), fit_par[0], np.sqrt(fit_cov[0,0]), weighted=True)
	y_hat, y_hat_err, chi_squared = lfit(x_hat, weighted=True)

	fig1 = plt.figure()
	ax1 = fig1.add_subplot(111)
	ax1.plot(x_hat, y_hat, label="Numpy curve fit", color="tab:blue")
	ax1.fill_between(x_hat, y_hat_err[0], y_hat_err[1], alpha=0.5, color="tab:blue")
	ax1.errorbar(x, signal_mean, yerr=signal_err, marker="o", label=r"Signal $\chi=%.2f$" % chi_squared, linestyle="none", color="tab:orange")
	ax1.set_ylim(0.5, 5)
	# ax1.axvline(x_fit, color="tab:orange")
	# ax1.fill_betweenx(np.linspace(0,6,100), x_fit_err[0], x_fit_err[1], label=r"$x_0\pm\sigma_{x_0}$", alpha=0.5, color="tab:orange")
	ax1.legend(loc="best", prop={"size":8})
	ax1.set_title("Fit test with curve_fit parameters")

	plt.show()
	# fit = LineFit(x, signal, signal_err)
	# x_hat = np.linspace(0, 5, 100)

def main():
	# _test_simple_line_fit()
	_test_inverse_line_fit()

if __name__ == '__main__':
	main()