from post_analysis.core.postcore import PostCore

class Topsus4PostAnalysis(PostCore):
	"""Post-analysis of the topsus with Q^4."""
	observable_name = r"$\chi(\langle Q^4 \rangle)^{1/8}$"
	observable_name_compact = "topsus4"
	x_label = r"$\sqrt{8t_{flow}}[fm]$"
	y_label = r"$\chi(\langle Q^4 \rangle)^{1/8} [GeV]$" # 1/8 correct?
	formula = (r"$\chi(\langle Q^4 \rangle)^{1/8} = \frac{\hbar}{aV^{1/4}} "
		"\langle Q^4 \rangle^{1/8} [GeV]$")

def __init__(self, *args, **kwargs):
	raise DeprecationWarning("Topsus4PostAnalysis is discontinued, as it does"
		" not make sense to perform this kind of analysis.")
	super(Topsus4PostAnalysis, self).__init__(*args, **kwargs)

def main():
	exit("Exit: Topsus4PostAnalysis not intended to be a standalone module.")

if __name__ == '__main__':
	main()