from core.topsusanalysercore import TopsusAnalyserCore
from core.euclideanintervalanalysercore import EuclideanIntervalAnalyser
import numpy as np

class TopsusteIntervalAnalyser(EuclideanIntervalAnalyser, TopsusAnalyserCore):
	"""
	Analysis where one can split the topological susceptibility in Euclidean
	time to obtain an estimate of the topological charge.
	"""
	observable_name = "Topological Susceptibility in Euclidean time"
	observable_name_compact = "topsuste"
	x_label = r"$\sqrt{8t_{flow}}[fm]$"
	y_label = r"$\chi^{1/4} [GeV]$"

	def __init__(self, *args, **kwargs):
		super(TopsusteIntervalAnalyser, self).__init__(*args, **kwargs)
		self.NT = self.y_original.shape[-1]
		self.observable_output_folder_path_old = self.observable_output_folder_path

	def set_t_interval(self, *args):
		"""Runs first the inherited time setter function, then its own."""
		super(TopsusteIntervalAnalyser, self).set_t_interval(*args)
		self.observable_name = r"$\chi(\langle Q^2 \rangle)^{1/4}$ in Euclidean time $[%d,%d)$" % self.t_interval
		self.NT_interval_size = self.t_interval[-1] - self.t_interval[0]
		self.V = self.lattice_sizes[self.beta] * self.NT_interval_size / float(self.NT)
		self.const = self.hbarc/self.a/self.V**(1./4)
		self.function_derivative_parameters = {"const": self.const}

		self.y = np.sum(self.y, axis=2)
		self.y **= 2
