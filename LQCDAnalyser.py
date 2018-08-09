#!/usr/bin/env python2

from pre_analysis.pre_analyser import pre_analysis
from post_analysis.post_analyser import post_analysis
from tools.folderreadingtools import get_num_observables
import copy
import os
import numpy as np


def main():
	#### Available observables
	observables = [
		"plaq", "energy",
		# Topological charge definitions
		# "topc2", "topc4",
		"topc", "topcMC", "topcr", "topcrMC",
		# Topological susceptibility definitions
		"topsus", "topsusMC", "topsusqtq0",
		# Other quantities 
		"topcr",
	]
	observables_euclidean_time = [
		# Topological charge
		"topct", "topcte",
		# Topological susceptiblity
		"topsust", "topsuste",
		# Other quantities 
		"qtq0e",
		"qtq0eff",
	]

	observables += observables_euclidean_time

	# obs_exlusions = ["plaq", "energy", "topc", "topc2", "topc4", "topcr", "topcMC", "topsus"]
	# obs_exlusions = ["energy", "topsus", "topsust", "topsuste", "topsusMC", "topsusqtq0"]
	# observables = list(set(set(observables) - set(obs_exlusions)))

	# observables = observables_euclidean_time
	# observables = ["topsus", "topsust", "topsuste", "topsusMC", "topsusqtq0"]
	# observables = ["topsusMC"]
	# observables = ["topcr", "qtq0eff"]
	# observables = ["topcte"]
	# observables = observables_euclidean_time
	# observables = ["topcr", "topsus"]
	# observables = ["topsust", "topsuste", "topsusqtq0"]
	# observables = ["topcrMC"]
	# observables = ["qtq0eff", "qtq0e"] + ["topsus", "topsust", "topsuste", "topsusMC", "topsusqtq0"]
	# observables = ["qtq0eff", "qtq0e"] + ["topsust", "topsuste", "topsusMC", "topsusqtq0"]
	# observables = ["topsus", "topsust", "topsuste", "topsusMC", "topsusqtq0"]
	# observables = ["topsusqtq0"]
	# observables = ["topsus"]
	# observables = ["qtq0effMC"]
	# observables = ["energy"]
	# observables = ["w_t_energy"]

	# observables += ["energy"]

	#### Base parameters
	N_bs = 500
	dryrun = False
	verbose = True
	print_latex = True
	parallel = True
	numprocs = 8
	section_seperator = "="*160

	#### Try to load binary file(much much faster)
	load_file = True

	# If we are to create per-flow datasets as opposite to per-cfg datasets
	create_perflow_data = False

	#### Save binary file
	save_to_binary = True

	#### Load specific parameters
	NFlows = 1000
	flow_epsilon = 0.01

	#### Post analysis parameters
	# run_post_analysis = True
	line_fit_interval_points = 20
	# topsus_fit_targets = [0.3,0.4,0.5,0.58]
	# topsus_fit_targets = [0.3, 0.4, 0.5, 0.6] # tf = sqrt(8*t0)
	topsus_fit_targets = [0.6]
	energy_fit_target = 0.3

	# Smearing gif parameters for qtq0e
	gif_params = {
		# "gif_observables": ["qtq0e", "qtq0eff"],
		"gif_observables": [], # Uncomment to turn off
		"gif_euclidean_time": 0.5,
		"gif_flow_range": np.linspace(0, 0.6, 100),
		"betas_to_plot": "all",
		"plot_together": False,
		"error_shape": "band",
	}

	#### Different batches
	# data_batch_folder = "../GluonAction/data8"
	data_batch_folder = "../GluonAction/data9"
	# data_batch_folder = "../GluonAction/DataGiovanni"
	# data_batch_folder = "../data/topc_modes_8x16"
	
	figures_folder = "figures"

	#### If we need to multiply
	if "DataGiovanni" in data_batch_folder:
		observables = set(set(observables) - set(observables_euclidean_time))
		observables = list(observables)
		correct_energy = False
		load_file = True
		save_to_binary = False
	else:
		correct_energy = True

	# Method of continuum extrapolation. 
	# Options: plateau, plateau_mean, nearest, interpolate, bootstrap
	extrapolation_methods = ["plateau", "plateau_mean", "nearest",
		"interpolate", "bootstrap"]
	extrapolation_methods = ["plateau"]
	extrapolation_methods = ["bootstrap"]
	plot_continuum_fit = False

	# Topcr reference value. Options: [float], t0beta, article, t0
	topcr_t0 = "t0beta"

	# Number of different sectors we will analyse in euclidean time
	numsplits_eucl = 4
	intervals_eucl = [None, None, None, None]

	# Number of different sectors we will analyse in monte carlo time
	MC_time_splits = 4
	# MC_intervals = [[0, 1000], [500, 1000], [500, 1000], [175, 250]]
	MC_intervals = [None, None, None, None]
 
	# Extraction point in flow time a*t_f for q0 in qtq0
	q0_flow_times = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6] # [fermi]

	# Flow time indexes in percent to plot qtq0 in euclidean time at
	euclidean_time_percents = [0, 0.25, 0.50, 0.75, 1.00]
	# euclidean_time_percents = [0]
	
	# Data types to be looked at in the post-analysis.
	post_analysis_data_type = ["bootstrap", "jackknife", "unanalyzed"]
	post_analysis_data_type = ["bootstrap"]

	#### Analysis batch setups
	default_params = {
		"N_bs": N_bs, 
		"dryrun": dryrun,
		"verbose": verbose, 
		"parallel": parallel,
		"numprocs": numprocs,
		"batch_folder": data_batch_folder,
		"figures_folder": figures_folder,
		"observables": observables,
		"load_file": load_file,
		"save_to_binary": save_to_binary, 
		# Flow parameters
		"create_perflow_data": create_perflow_data,
		"flow_epsilon": flow_epsilon, 
		"NFlows": NFlows,
		# Topc histogram parameters
		"topc_y_limits": None,
		"topc2_y_limits": None,
		"topc4_y_limits": None,
		"bin_range": [-10, 10],
		"num_bins_per_int": 4,
		"hist_flow_times": None,
		# Indexes to look at for topct.
		"num_t_euclidean_indexes": 5,
		# Interval selection parameters
		"q0_flow_times": q0_flow_times,
		"euclidean_time_percents": euclidean_time_percents,
		"numsplits_eucl": numsplits_eucl,
		"intervals_eucl": None,
		"MC_time_splits": MC_time_splits,
		"MCInt": None,
		# Various parameters
		"correct_energy": correct_energy,
		"print_latex": print_latex,
		# Gif smearing parameters in the qtq0e observable
		"gif": gif_params,
	}

	print section_seperator
	print "Observables to be analysed: %s" % ", ".join(observables)
	print section_seperator + "\n"

	########## Main analysis ##########
	databeta60 = copy.deepcopy(default_params)
	databeta60["batch_name"] = "beta60"
	databeta60["beta"] = 6.0
	databeta60["topc_y_limits"] = [-9, 9]
	databeta60["topc2_y_limits"] = [-81, 81]
	databeta60["NCfgs"] = get_num_observables(
		databeta60["batch_folder"],
		databeta60["batch_name"])
	databeta60["obs_file"] = "24_6.00"
	databeta60["MCInt"] = MC_intervals[0]
	databeta60["N"] = 24
	databeta60["NT"] = 2*databeta60["N"]
	databeta60["color"] = "#e41a1c"

	databeta61 = copy.deepcopy(default_params)
	databeta61["batch_name"] = "beta61"
	databeta61["beta"] = 6.1
	databeta61["topc_y_limits"] = [-12, 12]
	databeta61["topc2_y_limits"] = [-144, 144]
	databeta61["NCfgs"] = get_num_observables(
		databeta61["batch_folder"],
		databeta61["batch_name"])
	databeta61["obs_file"] = "28_6.10"
	databeta61["MCInt"] = MC_intervals[1]
	databeta61["N"] = 28
	databeta61["NT"] = 2*databeta61["N"]
	databeta61["color"] = "#377eb8"

	databeta62 = copy.deepcopy(default_params)
	databeta62["batch_name"] = "beta62"
	databeta62["beta"] = 6.2
	databeta62["topc_y_limits"] = [-12, 12]
	databeta62["topc2_y_limits"] = [-196, 196]
	databeta62["NCfgs"] = get_num_observables(
		databeta62["batch_folder"], 
		databeta62["batch_name"])
	databeta62["obs_file"] = "32_6.20"
	databeta62["MCInt"] = MC_intervals[2]
	databeta62["N"] = 32
	databeta62["NT"] = 2*databeta62["N"]
	databeta62["color"] = "#4daf4a"

	databeta645 = copy.deepcopy(default_params)
	databeta645["flow_epsilon"] = 0.02
	databeta645["batch_name"] = "beta645"
	databeta645["beta"] = 6.45
	databeta645["topc_y_limits"] = [-15, 15]
	databeta645["topc2_y_limits"] = [-300, 300]
	databeta645["NCfgs"] = get_num_observables(
		databeta645["batch_folder"],
		databeta645["batch_name"])
	databeta645["obs_file"] = "48_6.45"
	databeta645["MCInt"] = MC_intervals[3]
	databeta645["N"] = 48
	databeta645["NT"] = 2*databeta645["N"]
	databeta645["color"] = "#984ea3"

	########## Smaug data 8x16 analysis ##########
	smaug8x16_data_beta60_analysis = copy.deepcopy(default_params)
	smaug8x16_data_beta60_analysis["batch_folder"] = "../data/"
	smaug8x16_data_beta60_analysis["batch_name"] = "beta60_8x16_run"
	smaug8x16_data_beta60_analysis["beta"] = 6.0
	smaug8x16_data_beta60_analysis["topc_y_limits"] = [-2, 2]
	smaug8x16_data_beta60_analysis["num_bins_per_int"] = 32
	smaug8x16_data_beta60_analysis["bin_range"] = [-2.5, 2.5]
	smaug8x16_data_beta60_analysis["hist_flow_times"] = [0, 250, 600]
	smaug8x16_data_beta60_analysis["NCfgs"] = get_num_observables(
		smaug8x16_data_beta60_analysis["batch_folder"], 
		smaug8x16_data_beta60_analysis["batch_name"])
	smaug8x16_data_beta60_analysis["obs_file"] = "8_6.00"
	smaug8x16_data_beta60_analysis["N"] = 8
	smaug8x16_data_beta60_analysis["NT"] = 16
	smaug8x16_data_beta60_analysis["color"] = "#377eb8"

	########## Smaug data 12x24 analysis ##########
	smaug12x24_data_beta60_analysis = copy.deepcopy(default_params)
	smaug12x24_data_beta60_analysis["batch_folder"] = "../data/"
	smaug12x24_data_beta60_analysis["batch_name"] = "beta60_12x24_run"
	smaug12x24_data_beta60_analysis["beta"] = 6.0
	smaug12x24_data_beta60_analysis["topc_y_limits"] = [-4, 4]
	smaug12x24_data_beta60_analysis["num_bins_per_int"] = 16
	smaug12x24_data_beta60_analysis["bin_range"] = [-4.5, 4.5]
	smaug12x24_data_beta60_analysis["hist_flow_times"] = [0, 250, 600]
	smaug12x24_data_beta60_analysis["NCfgs"] = get_num_observables(
		smaug12x24_data_beta60_analysis["batch_folder"], 
		smaug12x24_data_beta60_analysis["batch_name"])
	smaug12x24_data_beta60_analysis["obs_file"] = "12_6.00"
	smaug12x24_data_beta60_analysis["N"] = 12
	smaug12x24_data_beta60_analysis["NT"] = 24
	smaug12x24_data_beta60_analysis["color"] = "#377eb8"

	########## Smaug data 16x32 analysis ##########
	smaug16x32_data_beta61_analysis = copy.deepcopy(default_params)
	smaug16x32_data_beta61_analysis["batch_folder"] = "../data/"
	smaug16x32_data_beta61_analysis["batch_name"] = "beta61_16x32_run"
	smaug16x32_data_beta61_analysis["beta"] = 6.1
	smaug16x32_data_beta61_analysis["topc_y_limits"] = [-8, 8]
	smaug16x32_data_beta61_analysis["num_bins_per_int"] = 16
	smaug16x32_data_beta61_analysis["bin_range"] = [-7.5, 7.5]
	smaug16x32_data_beta61_analysis["hist_flow_times"] = [0, 250, 600]
	smaug16x32_data_beta61_analysis["NCfgs"] = get_num_observables(
		smaug16x32_data_beta61_analysis["batch_folder"], 
		smaug16x32_data_beta61_analysis["batch_name"])
	smaug16x32_data_beta61_analysis["obs_file"] = "16_6.10"
	smaug16x32_data_beta61_analysis["N"] = 16
	smaug16x32_data_beta61_analysis["NT"] = 32
	smaug16x32_data_beta61_analysis["color"] = "#377eb8"

	########## Distribution analysis ##########
	dist_eps = [0.05, 0.10, 0.20, 0.24, 0.30, 0.40, 0.60]
	def create_dist_batch_set(default_parameters, eps):
		clean_str = lambda s: str("%-2.2f"%s).replace(".", "")
		dist_data_beta60_analysis = copy.deepcopy(default_parameters)
		dist_data_beta60_analysis["batch_folder"] = (
			"../data/distribution_tests/distribution_runs")
		dist_data_beta60_analysis["batch_name"] = \
			"distribution_test_eps{0:s}".format(clean_str(eps))
		dist_data_beta60_analysis["beta"] = 6.0
		dist_data_beta60_analysis["num_bins_per_int"] = 16
		dist_data_beta60_analysis["bin_range"] = [-2.1, 2.1]
		dist_data_beta60_analysis["hist_flow_times"] = [0, 250, 600]
		dist_data_beta60_analysis["NCfgs"] = get_num_observables(
			dist_data_beta60_analysis["batch_folder"],
			dist_data_beta60_analysis["batch_name"])
		dist_data_beta60_analysis["obs_file"] = "6_6.00" # 6^3x12, beta=6.0
		dist_data_beta60_analysis["N"] = 6
		dist_data_beta60_analysis["NT"] = 12
		dist_data_beta60_analysis["color"] = "#377eb8"
		return dist_data_beta60_analysis

	dist_param_list = [create_dist_batch_set(default_params, _eps)
		for _eps in dist_eps]

	# #### Submitting distribution analysis
	# analysis_parameter_list = dist_param_list
	# for analysis_parameters in analysis_parameter_list:
	# 	pre_analysis(analysis_parameters)

	# #### Submitting 8x16 analysis
	# analysis_parameter_list = [smaug8x16_data_beta60_analysis]
	# for analysis_parameters in analysis_parameter_list:
	# 	pre_analysis(analysis_parameters)

	# #### Submitting 12x24 analysis
	# analysis_parameter_list = [smaug12x24_data_beta60_analysis]
	# for analysis_parameters in analysis_parameter_list:
	# 	pre_analysis(analysis_parameters)

	# #### Submitting 16x32 analysis
	# analysis_parameter_list = [smaug16x32_data_beta61_analysis]
	# for analysis_parameters in analysis_parameter_list:
	# 	pre_analysis(analysis_parameters)

	### Adding relevant batches to args
	analysis_parameter_list = [databeta60, databeta61, databeta62, databeta645]
	# analysis_parameter_list = [databeta60, databeta61, databeta62]
	# analysis_parameter_list = [databeta61, databeta62]
	# analysis_parameter_list = [databeta62]
	# analysis_parameter_list = [databeta645]

	#### Submitting main analysis
	for analysis_parameters in analysis_parameter_list:
		pre_analysis(analysis_parameters)

	if not analysis_parameter_list[0]["MCInt"] is None:
		assert sum([len(plist["MCInt"]) - len(analysis_parameter_list[0]["MCInt"])
			for plist in analysis_parameter_list]) == 0, \
			"unequal amount of MC intervals"

	#### Submitting post-analysis data
	if len(analysis_parameter_list) >= 3:
		post_analysis(analysis_parameter_list, observables,
			topsus_fit_targets, line_fit_interval_points, energy_fit_target,
			q0_flow_times, euclidean_time_percents,
			extrapolation_methods=extrapolation_methods,
			plot_continuum_fit=plot_continuum_fit,
			post_analysis_data_type=post_analysis_data_type,
			figures_folder=figures_folder, gif_params=gif_params, 
			verbose=verbose)
	else:
		msg = "Need at least 3 different beta values to run post analysis"
		msg += "(%d given)."% len(analysis_parameter_list)
		print msg

if __name__ == '__main__':
	main()