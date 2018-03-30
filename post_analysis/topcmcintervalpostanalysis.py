from core.multiplotcore import MultiPlotCore

class TopcMCIntervalPostAnalysis(MultiPlotCore):
	"""Post-analysis of the topological charge in MC time intervals."""
	observable_name = "Topological Charge in MC time intervals"
	observable_name_compact = "topcMC"
	x_label = r"$\sqrt{8t_{flow}}[fm]$"
	y_label = r"$Q$"
	sub_obs = True

def main():
	exit("Exit: TopcMCIntervalPostAnalysis not intended to be a standalone module.")

if __name__ == '__main__':
	main()