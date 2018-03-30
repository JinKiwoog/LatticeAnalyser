from core.postcore import PostCore


class PlaqPostAnalysis(PostCore):
	"""Post-analysis of the topological charge."""
	observable_name = "Plaquette"
	observable_name_compact = "plaq"
	y_label = r"$P$"
	x_label = r"$\sqrt{8t}$[fm]"
	formula = r"$P = \frac{1}{16V} \sum_{x,\mu,\nu} \tr\mathcal{Re} P_{\mu\nu}$"


def main():
	exit("Exit: PlaqPostAnalysis not intended to be a standalone module.")


if __name__ == '__main__':
	main()