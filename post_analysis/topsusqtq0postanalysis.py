from core.multiplotcore import MultiPlotCore
from core.topsuscore import TopsusCore
from tools.folderreadingtools import check_folder
import os

class TopsusQtQ0PostAnalysis(MultiPlotCore, TopsusCore):
	"""Post-analysis of the topsus at a fixed flow time."""
	observable_name = r"$\chi(\langle Q_t Q_{t_0} \rangle)^{1/4}$"
	observable_name_compact = "topsusqtq0"
	x_label = r"$\sqrt{8t_{flow}}[fm]$"
	y_label = r"$\chi(\langle Q_{t} Q_{t_0} \rangle)^{1/4} [GeV]$" # $\chi_t^{1/4}[GeV]$
	sub_obs = True

	# Continuum plot variables
	y_label_continuum = r"$\chi^{1/4}(\langle Q_{t} Q_{t_0} \rangle)[GeV]$"

	def plot_continuum(self, fit_target, interval_index, title_addendum=""):
		# Backs up old variables
		self.plot_values_old = self.plot_values
		self.output_folder_path_old = self.output_folder_path

		# Sets plot values
		data = self._get_analysis_data(self.analysis_data_type)
		self._initiate_plot_values(data, interval_index=interval_index)

		t_flow = float(sorted(self.plot_values.values())[0]["interval"])/100 # To normalize the flow

		self.output_folder_path = os.path.join(self.output_folder_path, "t%d" % t_flow)
		check_folder(self.output_folder_path, False, self.verbose)
		title_addendum = r", $t_{flow}=%.2f$" % t_flow
		super(TopsusQtQ0PostAnalysis, self).plot_continuum(fit_target, title_addendum=title_addendum)

		# Resets the plot values and output folder path
		self.plot_values = self.plot_values_old
		self.output_folder_path = self.output_folder_path_old

	def _convert_label(self, label):
		"""Short method for formatting time in labels."""
		try:
			return r"$t_{flow}=%.2f$" % (float(label)/100)
		except ValueError:
			return r"$%s$" % label

def main():
	exit("Exit: TopsusQtQ0PostAnalysis not intended to be a standalone module.")

if __name__ == '__main__':
	main()