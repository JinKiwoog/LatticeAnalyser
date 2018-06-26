from observable_analysis import *
from tools.folderreadingtools import DataReader
from tools.analysis_setup_tools import get_intervals
import time
import numpy as np
import types
from tqdm import tqdm


def analyse_default(analysis_object, N_bs, NBins=None, skip_histogram=False,
	bs_index_lists=None):
	"""Default analysis method for pre-analysis."""
	print analysis_object
	analysis_object.boot(N_bs, index_lists=bs_index_lists)
	analysis_object.jackknife()
	analysis_object.save_post_analysis_data()
	analysis_object.plot_original()
	analysis_object.plot_boot()
	analysis_object.plot_jackknife()
	analysis_object.autocorrelation()
	analysis_object.plot_autocorrelation(0)
	analysis_object.plot_autocorrelation(-1)
	analysis_object.plot_mc_history(0)
	analysis_object.plot_mc_history(int(analysis_object.NFlows * 0.25))
	analysis_object.plot_mc_history(int(analysis_object.NFlows * 0.50))
	analysis_object.plot_mc_history(int(analysis_object.NFlows * 0.75))
	analysis_object.plot_mc_history(-1)
	analysis_object.plot_original()
	analysis_object.plot_boot()
	analysis_object.plot_jackknife()
	if not skip_histogram:
		# Plots histogram at the beginning, during and end.
		hist_pts = [0, 
			int(analysis_object.NFlows * 0.25), 
			int(analysis_object.NFlows * 0.50), 
			int(analysis_object.NFlows * 0.75), -1
		]
		for iHist in hist_pts:
			analysis_object.plot_histogram(iHist, NBins=NBins)
		analysis_object.plot_multihist([hist_pts[0], hist_pts[2], 
			hist_pts[-1]], NBins=NBins)
	analysis_object.plot_integrated_correlation_time()
	analysis_object.save_post_analysis_data() # save_as_txt=False

def gif_analysis(gif_analysis_obj, gif_flow_range, N_bs, 
	gif_euclidean_time=None):
	"""Function for creating gifs as effectively as possible."""

	# Sets up random boot strap lists so they are equal for all flow times
	NCfgs = gif_analysis_obj.N_configurations
	bs_index_lists = np.random.randint(NCfgs, size=(N_bs, NCfgs))

	# Runs basic data analysis
	gif_descr = "Data creation for %s gif" \
		% gif_analysis_obj.observable_name_compact
	for iFlow in tqdm(gif_flow_range, desc=gif_descr):
		if isinstance(gif_euclidean_time, types.NoneType):
			gif_analysis_obj.set_time(iFlow)
		else:
			gif_analysis_obj.set_time(iFlow, gif_euclidean_time)
		gif_analysis_obj.boot(N_bs, index_lists=bs_index_lists)
		gif_analysis_obj.autocorrelation()
		gif_analysis_obj.save_post_analysis_data()

def analyse_plaq(params):
	"""Analysis of the plaquette."""
	# obs_data, dryrun, parallel, numprocs, verbose, N_bs = params 
	plaq_analysis = PlaquetteAnalyser(params["data"]("plaq"), 
		dryrun=params["dryrun"], parallel=params["parallel"], 
		numprocs=params["numprocs"], verbose=params["verbose"])
	analyse_default(plaq_analysis, params["N_bs"])

def analyse_energy(params):
	"""Analysis of the energy.""" 
	energy_analysis = EnergyAnalyser(params["data"]("energy"), 
		dryrun=params["dryrun"], parallel=params["parallel"], 
		numprocs=params["numprocs"], verbose=params["verbose"])
	analyse_default(energy_analysis, params["N_bs"])

def analyse_topsus(params):
	"""Analysis of topsus."""
	topsus_analysis = TopsusAnalyser(params["data"]("topc"), 
		dryrun=params["dryrun"], parallel=params["parallel"], 
		numprocs=params["numprocs"], verbose=params["verbose"])
	analyse_default(topsus_analysis, params["N_bs"])

def analyse_topc(params):
	"""Analysis of Q."""
	topc_analysis = TopcAnalyser(params["data"]("topc"), 
		dryrun=params["dryrun"], parallel=params["parallel"], 
		numprocs=params["numprocs"], verbose=params["verbose"])

	if topc_analysis.beta == 6.0:
		topc_analysis.y_limits = [-9, 9]
	elif topc_analysis.beta == 6.1:
		topc_analysis.y_limits = [-12, 12]
	elif topc_analysis.beta == 6.2:
		topc_analysis.y_limits = [-12, 12]
	else:
		topc_analysis.y_limits = [None, None]

	analyse_default(topc_analysis, params["N_bs"])

def analyse_topc2(params):
	"""Analysis of Q^2."""
	topc2_analysis = Topc2Analyser(params["data"]("topc"), 
		dryrun=params["dryrun"], parallel=params["parallel"], 
		numprocs=params["numprocs"], verbose=params["verbose"])

	if topc2_analysis.beta == 6.0:
		topc2_analysis.y_limits = [-81, 81]
	elif topc2_analysis.beta == 6.1:
		topc2_analysis.y_limits = [-144, 144]
	elif topc2_analysis.beta == 6.2:
		topc2_analysis.y_limits = [-196, 196]
	else:
		topc2_analysis.y_limits = [None, None]

	analyse_default(topc2_analysis, params["N_bs"], NBins=150)

def analyse_topc4(params):
	"""Analysis the topological chage with q^4."""
	topc4_analysis = Topc4Analyser(params["data"]("topc"), 
		dryrun=params["dryrun"], parallel=params["parallel"], 
		numprocs=params["numprocs"], verbose=params["verbose"])
	analyse_default(topc4_analysis, params["N_bs"])

def analyse_topcr(params):
	"""
	Analysis of the ratio with R=q4c/q2 of the topological charge. Performs an
	analysis on Q^2 and Q^4 with the same bootstrap samples, such that an post
	analysis can be performed on these explisitly.
	"""
	topc2_analysis = Topc2Analyser(params["data"]("topc"), 
		dryrun=params["dryrun"], parallel=params["parallel"], 
		numprocs=params["numprocs"], verbose=params["verbose"])
	topc4_analysis = Topc4Analyser(params["data"]("topc"), 
		dryrun=params["dryrun"], parallel=params["parallel"], 
		numprocs=params["numprocs"], verbose=params["verbose"])

	N_cfgs_topc2 = topc2_analysis.N_configurations
	N_cfgs_topc4 = topc4_analysis.N_configurations
	assert N_cfgs_topc2 == N_cfgs_topc4, "NCfgs differ in topc2 and topc4."

	N_bs = params["N_bs"]
	bs_index_lists = np.random.randint(N_cfgs_topc2,
		size=(N_bs, N_cfgs_topc2))

	analyse_default(topc2_analysis, N_bs, NBins=150, 
		bs_index_lists=bs_index_lists)
	analyse_default(topc4_analysis, N_bs, bs_index_lists=bs_index_lists)

def analyse_topsus_qtq0(params):
	"""
	Analysis the topological susceptiblity with one charge q0 set a given 
	flow time.
	"""
	topsus_qtq0_analysis = TopsusQtQ0Analyser(params["data"]("topc"), 
		dryrun=params["dryrun"], parallel=params["parallel"], 
		numprocs=params["numprocs"], verbose=params["verbose"])

	for q0_flow_time in params["q0_flow_times"]:
		topsus_qtq0_analysis.setQ0(q0_flow_time) 
		analyse_default(topsus_qtq0_analysis, params["N_bs"], 
			skip_histogram=True)

def analyse_qtq0e(params):
	"""Analysis for the effective mass qtq0 with q0 at a fixed flow time."""
	obs_data = params["data"]
	if not obs_data.has_observable("topct"): return

	qtq0_analysis = QtQ0EuclideanAnalyser(obs_data("topct"), 
		dryrun=params["dryrun"], parallel=params["parallel"], 
		numprocs=params["numprocs"], verbose=params["verbose"])

	for q0_flow_time in param["q0_flow_times"]:
		for euclidean_percent in params["euclidean_time_percents"]:
			qtq0_analysis.set_time(q0_flow_time, euclidean_percent)
			analyse_default(qtq0_analysis, params["N_bs"])

def analyse_qtq0_effective_mass(params):
	"""
	Pre-analyser for the effective mass qtq0 with q0 at a fixed flow time.
	"""

	obs_data = params["data"]
	if not obs_data.has_observable("topct"): return

	qtq0eff_analysis = QtQ0EffectiveMassAnalyser(obs_data("topct"), 
		dryrun=params["dryrun"], parallel=params["parallel"], 
		numprocs=params["numprocs"], verbose=params["verbose"])

	for q0_flow_time in param["q0_flow_times"]:
		if q0_flow_time != 0.6: # Only zeroth flow 
			continue
		qtq0eff_analysis.set_time(q0_flow_time)
		analyse_default(qtq0eff_analysis, params["N_bs"])

def analyse_topct(params):
	"""Analyses topological charge at a specific euclidean time."""

	obs_data = params["data"]
	if not obs_data.has_observable("topct"): return

	topct_analysis = TopctAnalyser(obs_data("topct"), 
		dryrun=params["dryrun"], parallel=params["parallel"], 
		numprocs=params["numprocs"], verbose=params["verbose"])

	indexes = np.linspace(0, topct_analysis.NT, 
		params["num_t_euclidean_indexes"], dtype=int)
	indexes -= 1
	indexes[0] += 1

	for ie in indexes:
		topct_analysis.setEQ0(ie)
		analyse_default(topct_analysis, params["N_bs"])

def analyse_topsust(params):
	"""Analyses topological susceptibility at a specific euclidean time."""

	obs_data = params["data"]
	if not obs_data.has_observable("topct"): return

	topct_analysis = TopsustAnalyser(obs_data("topct"), 
		dryrun=params["dryrun"], parallel=params["parallel"], 
		numprocs=params["numprocs"], verbose=params["verbose"])

	indexes = np.linspace(0, topct_analysis.NT, 
		params["num_t_euclidean_indexes"], dtype=int)
	indexes -= 1
	indexes[0] += 1
	for ie in indexes:
		topct_analysis.setEQ0(ie)
		analyse_default(topct_analysis, N_bs, skip_histogram=True)

def analyse_topcte_intervals(params):
	"""
	Analysis function for the topological charge in euclidean time intervals. 
	Requires either numsplits or intervals.

	Args:
		params: list of default parameters containing obs_data, dryrun, 
			parallel, numprocs, verbose, N_bs.
		numsplits: number of splits to make in the dataset. Default is None.
		intervals: intervals to plot in. Default is none.
	"""

	obs_data = params["data"]
	if not obs_data.has_observable("topct"): return

	t_interval, _ = get_intervals(obs_data.NT,
		numsplits=params["numsplits_eucl"],
		intervals=params["intervals_eucl"])

	analyse_topcte = TopcteIntervalAnalyser(obs_data("topct"), 
		dryrun=params["dryrun"], parallel=params["parallel"], 
		numprocs=params["numprocs"], verbose=params["verbose"])

	for t_int in t_interval:
		analyse_topcte.set_t_interval(t_int)
		analyse_default(analyse_topcte, params["N_bs"])

def analyse_topsuste_intervals(params):
	"""
	Analysis function for the topological susceptibility in euclidean time. 
	Requires either numsplits or intervals.

	Args:
		params: list of default parameters containing obs_data, dryrun, 
			parallel, numprocs, verbose, N_bs.
		numsplits: number of splits to make in the dataset. Default is None.
		intervals: intervals to plot in. Default is none.
	"""

	obs_data = params["data"]
	if not obs_data.has_observable("topct"): return

	t_interval, _ = get_intervals(obs_data.NT, 
		numsplits=params["numsplits_eucl"],
		intervals=params["intervals_eucl"])

	analyse_topsuste = TopsusteIntervalAnalyser(obs_data("topct"), 
		dryrun=params["dryrun"], parallel=params["parallel"], 
		numprocs=params["numprocs"], verbose=params["verbose"])

	for t_int in t_interval:
		analyse_topsuste.set_t_interval(t_int)
		analyse_default(analyse_topsuste, params["N_bs"])

def analyse_topcMCTime(params):
	"""Analysis the topological charge in monte carlo time slices."""
	obs_data = params["data"]
	MC_interval, interval_size = get_intervals(obs_data.NCfgs, 
		numsplits=params["MC_time_splits"], intervals=params["MCInt"])

	bs_index_lists = np.random.randint(interval_size,
		size=(N_bs, interval_size))

	for MC_int in MC_interval:
		analyse_topcMC = TopcMCIntervalAnalyser(obs_data("topc"),
			mc_interval=MC_int, dryrun=params["dryrun"], 
			parallel=params["parallel"], numprocs=params["numprocs"],
			verbose=params["verbose"])

		analyse_default(analyse_topcMC, params["N_bs"], 
			bs_index_lists=bs_index_lists)

def analyse_topsusMCTime(params):
	"""Analysis the topological susceptibility in monte carlo time slices."""

	obs_data = params["data"]
	MC_interval, interval_size = get_intervals(obs_data.NCfgs,
		numsplits=params["MC_time_splits"], intervals=params["MCInt"])

	bs_index_lists = np.random.randint(interval_size,
		size=(params["N_bs"], interval_size))

	for MC_int in MC_interval:
		analyse_topcMC = TopsusMCIntervalAnalyser(obs_data("topc"),
			mc_interval=MC_int, dryrun=params["dryrun"], 
			parallel=params["parallel"], numprocs=params["numprocs"],
			verbose=params["verbose"])

		analyse_default(analyse_topcMC, params["N_bs"],
			bs_index_lists=bs_index_lists)

def pre_analysis(parameters):
	"""
	Function for starting flow analyses.

	Args:
		parameters: dictionary containing following elements: batch_name, 
			batch_folder, observables, NCfgs, obs_file, load_file, 
			save_to_binary, base_parameters, flow_epsilon, NFlows,
			create_perflow_data, correct_energy
	"""

	# Analysis timers
	pre_time = time.clock()
	observable_strings = []

	# Retrieves analysis parameters
	batch_name = parameters["batch_name"]
	batch_folder = parameters["batch_folder"]
	figures_folder = parameters["figures_folder"]
	parameters["lattice_size"] = parameters["N"]**3*parameters["NT"]

	# Retrieves data
	obs_data = DataReader(batch_name, batch_folder, figures_folder, 
		load_binary_file=parameters["load_file"],
		save_to_binary=parameters["save_to_binary"],
		flow_epsilon=parameters["flow_epsilon"], NCfgs=parameters["NCfgs"],
		create_perflow_data=parameters["create_perflow_data"],
		correct_energy=parameters["correct_energy"],
		lattice_size=parameters["lattice_size"], verbose=parameters["verbose"],
		dryrun=parameters["dryrun"])

	# Writes a parameters file for the post analysis
	obs_data.write_parameter_file()

	print "="*160

	# Builds parameters list to be passed to analyser
	# params = [obs_data, _bp["dryrun"], _bp["parallel"], _bp["numprocs"], 
	# 	_bp["verbose"], _bp["N_bs"]]
	params = {"data": obs_data}
	params.update(parameters)

	# Runs through the different observables and analyses each one
	if "plaq" in parameters["observables"]:
		analyse_plaq(params)
	if "energy" in parameters["observables"]:
		analyse_energy(params)

	# Topological charge definitions
	if "topc" in parameters["observables"]:
		analyse_topc(params)
	if "topc2" in parameters["observables"]:
		analyse_topc2(params)
	if "topc4" in parameters["observables"]:
		analyse_topc4(params)
	if "topcr" in parameters["observables"]:
		analyse_topcr(params)
	if "topct" in parameters["observables"]:
		analyse_topct(params)
	if "topcte" in parameters["observables"]:
		analyse_topcte_intervals(params)
	if "topcMC" in parameters["observables"]:
		analyse_topcMCTime(params)

	# Topological susceptibility definitions
	if "topsus" in parameters["observables"]:
		analyse_topsus(params)
	if "topsust" in parameters["observables"]:
		analyse_topsust(params)
	if "topsuste" in parameters["observables"]:
		analyse_topsuste_intervals(params)
	if "topsusMC" in parameters["observables"]:
		analyse_topsusMCTime(params)
	if "topsusqtq0" in parameters["observables"]:
		analyse_topsus_qtq0(params)

	# Other definitions
	if "qtq0e" in parameters["observables"]:
		analyse_qtq0e(param)
	if "qtq0eff" in parameters["observables"]:
		analyse_qtq0_effective_mass(params)

	gif_params = parameters["gif"]
	gif_observables = gif_params["gif_observables"]
	gif_euclidean_time = gif_params["gif_euclidean_time"]
	gif_flow_range = gif_params["gif_flow_range"]
	if len(gif_observables) != 0:
		obs_data, dryrun, parallel, numprocs, verbose, N_bs = params

		if "qtq0e" in gif_observables:
			qtq0e_gif_analysis = QtQ0EGif(obs_data("topct"), 
				dryrun=dryrun, parallel=parallel, numprocs=numprocs, 
				verbose=False)
			gif_analysis(qtq0e_gif_analysis, gif_flow_range, N_bs, 
				gif_euclidean_time=gif_euclidean_time)
		
		if "qtq0eff" in gif_observables:
			qtq0eff_gif_analysis = QtQ0EffGif(obs_data("topct"),
				dryrun=dryrun, parallel=parallel, numprocs=numprocs, 
				verbose=False)
			gif_analysis(qtq0eff_gif_analysis, gif_flow_range, N_bs,
				gif_euclidean_time=None)


	post_time = time.clock()
	print "="*160
	print "Analysis of batch %s observables %s in %.2f seconds" % (batch_name,
		", ".join([i.lower() for i in parameters["observables"]]),
		(post_time-pre_time))
	print "="*160

def main():
	exit("No default run for pre_analyser.py is currently set up.")

if __name__ == '__main__':
	main()