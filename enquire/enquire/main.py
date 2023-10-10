from .ppi import *
from .steinerdiv import ExpMinMaxDiverseSteinerTreeComputer
import networkx as nx
import os.path
import warnings
import pandas as pd

import os
import sys
import numpy as np 
import pandas as pd
import subprocess
import glob 
import re
#
try:
	import _pickle as pickle
except ModuleNotFoundError:
	import pickle
#
# Pickle a file and then compress it into a file with extension 
def compress_pickle(title, data):
	with bz2.BZ2File(title + ".pbz2", "w") as f: 
		pickle.dump(data, f)
#
# decompress .pbz2 file to a variable
def decompress_pickle(file):
	data = bz2.BZ2File(file, "rb") 
	data = pickle.load(data)
	return data
	#	
# Literature Data and all other edge/node tables #
def globtab(globbing):	
	litlinksfile=glob.glob(globbing)
	litlinksdata=[pd.read_csv(f,sep='\t') for f in litlinksfile]
	# regex names # 
	expind=[re.findall("^([^/]+)\\/(.*subgraphs_expansion)?([0-9]?[0-9]?)",s)[0][-1] for s in litlinksfile]
	expind=[int(x) if bool(re.search('[0-9]+',x)) else 0 for x in expind]
	return {k:v for k,v in zip(expind,litlinksdata)} 
#	
# subgraphs 
def globtabsub(globbing):	
	litlinksfile=glob.glob(globbing)
	litlinksdata=[pd.read_csv(f,sep='\t') for f in litlinksfile]
	# regex names # 
	expind=[re.findall("^([^/]+)\\/(.*subgraphs_expansion)?([0-9]?[0-9]?)",s)[0][-1] for s in litlinksfile]
	expind=[int(x) if bool(re.search('[0-9]+',x)) else 0 for x in expind]
	#
	subid=[int(re.findall("^.+_([0-9]+)\\.tsv$",s)[0][-1]) for s in litlinksfile]
	#
	tabl=pd.DataFrame({'Expansion':expind,'SubgraphId':subid,'File':litlinksfile})
	# nested table of subgraphs tables 
	return tabl.groupby('Expansion').apply(lambda x: {k:pd.read_csv(v,sep='\t') for k,v in zip(x.SubgraphId,x.File)}).to_dict()

# tag,to_py,thr=1,wd="$(pwd)/",comb=4,A=2,K=3,etype='all',rscript="/home/musellla/miniconda3/envs/R363/bin/Rscript",ncores=32

# wd='$(pwd)/'
# tag='SplicingFactors_Neoplasms_Antigens'
# ncores=32
# K=3
# A=2
# thr=2
# comb=4
# to_py='pmid-rnasplicin-antigens-set.txt'
# etype='all'
# rscript='/home/musellla/miniconda3/envs/R363/bin/Rscript'

# ---------------------------------------------------------------------------------------------------------------------------------------------

def run(tag, to_py, seeds, network='BioGRID', namespace='GENE_SYMBOL', alpha=0.25, beta=0.9, n=30, tau=0.1, study_bias_scores=None, gamma=1.0, outfile=None):
    is_graphml=0
    # Check the namespace and parse the network.
    namespace = _check_namespace(namespace)
    network,is_graphml=_check_and_preprocess_network(network, namespace)
    network = read_ppi_network(network, is_graphml)

    # Parse the study bias scores if provided and set the edge weights.
    if study_bias_scores is None:
        edge_weights = UnitEdgeWeight()
    # elif study_bias_scores=='None':
    #     edge_weights = UnitEdgeWeight()
    else:
        path_to_study_bias_scores = _get_path_to_study_bias_scores(study_bias_scores, namespace)
        if path_to_study_bias_scores=='None':
            edge_weights = UnitEdgeWeight()
        else:
            add_study_bias_scores_to_network(path_to_study_bias_scores, network)
            gamma = _check_gamma(gamma)
            edge_weights = BiasAwareEdgeWeight(network, gamma)
    

    # Kick out seeds not in network.
    terminals = _get_terminals(seeds)
    terminals = list(set(terminals).intersection(set(network.nodes)))


    # Set up instance and engine.
    ppi_instance = PPIInstance(network, terminals, edge_weights)
    engine = ExpMinMaxDiverseSteinerTreeComputer(initial_fraction=alpha, reduction_factor=beta)

    # Compute the module.
    steiner_trees = engine(ppi_instance, n=n)
    module_as_df = steiner_trees.get_occurrences(include_terminals=True)
    # module_as_df.to_csv('module_as_df_original.txt', index=False) # --> Check original output nodes.

    module_as_df = module_as_df[module_as_df["%occurrences"] >= tau]
    # module_as_df.to_csv('module_as_df.txt', index=False) # --> Check final output nodes. [Orignal_nodes - final_nodes = deleted_nodes]

    module_as_subgraph = steiner_trees.get_subgraph(threshold=tau)

    # Add connected component ID to nodes contained in module.
    comp_idx = 0
    for comp in sorted(nx.connected_components(module_as_subgraph), key=len, reverse=True):
        for node in comp:
            module_as_subgraph.nodes[node]['connected_components_id'] = comp_idx
        comp_idx += 1

    # Save module if requested.
    if outfile is not None:
        _save_module(module_as_df, module_as_subgraph, outfile)

    # Return module.
    return module_as_df, module_as_subgraph


def _check_namespace(namespace):
    if namespace not in ['GENE_SYMBOL', 'ENTREZ', 'UNIPROT', 'ENSEMBL']:
        warnings.warn(f'Illegal value {namespace} for parameter "namespace".\n'
                      f'==> Setting parameter "namespace" to "GENE_SYMBOL"')
        namespace = 'GENE_SYMBOL'
    return namespace


def _get_path_to_study_bias_scores(study_bias_scores, namespace):
    if isinstance(study_bias_scores, pd.DataFrame):
        study_bias_scores.to_csv(f'robust_bias_aware/data/study_bias_scores/{namespace}/custom_study_bias_scores.csv', index=False)
        study_bias_scores=f'robust_bias_aware/data/study_bias_scores/{namespace}/custom_study_bias_scores.csv'
        return study_bias_scores
    else:
        if os.path.exists(study_bias_scores):
            return study_bias_scores
        if study_bias_scores not in ['None','BAIT_USAGE', 'STUDY_ATTENTION']:
            warnings.warn(f'Illegal value {study_bias_scores} for parameter "study_bias_scores".\n'
                        f'==> Setting parameter "study_bias_scores" to "BAIT_USAGE"')
            study_bias_scores = 'BAIT_USAGE'
        else:
            if study_bias_scores=='None':
                return study_bias_scores
    return f'robust_bias_aware/data/study_bias_scores/{namespace}/{study_bias_scores}.csv'


def _check_and_preprocess_network(network, namespace):
    is_graphml=0
    if type(network) is nx.Graph:
        is_graphml=1
    elif type(network) is str:
        if network.endswith('.graphml'):
            is_graphml=1
            network=nx.read_graphml(network)
        elif network in ['BioGRID', 'APID', 'STRING']:
            network = f'robust_bias_aware/data/networks/{namespace}/{network}.txt'
        elif (network.endswith('.txt') or network.endswith('.csv') or network.endswith('.tsv')):
            if not os.path.exists(network):
                raise ValueError(f'Illegal network type: {network}')
        else:
            raise ValueError(f'Illegal network type: {network}')
    elif isinstance(network, pd.DataFrame):
        network.to_csv(f'robust_bias_aware/data/networks/{namespace}_customNetwork.txt', index=False, sep=' ')
        network=f'robust_bias_aware/data/networks/{namespace}_customNetwork.txt'
    return network, is_graphml


def _check_gamma(gamma):
    if gamma > 1:
        warnings.warn(f'Illegal value {gamma} > 1 for parameter "gamma".\n'
                      f'==> Setting parameter "gamma" to 1.0')
        gamma = 1.0
    if gamma < 0:
        warnings.warn(f'Illegal value {gamma} < 0 for parameter "gamma".\n'
                      f'==> Setting parameter "gamma" to 0.0')
        gamma = 0.0
    return gamma


def _get_terminals(seeds):
    if type(seeds) == str:
        if os.path.exists(seeds):
            seeds = read_terminals(seeds)
        else:
            raise ValueError(f'Illegal value {seeds} for parameter "seeds".\n'
                             f'Must be a valid path.')
    else:
        if not type(seeds) == list:
            raise ValueError(f'Illegal value {seeds} for parameter "seeds".\n'
                             f'Must be a valid path.')
    return seeds


def _save_module(solution_as_df, subgraph, outfile):
    if outfile.endswith(".csv"):
        solution_as_df.to_csv(outfile)
    elif outfile.endswith(".graphml"):
        nx.write_graphml(subgraph, outfile)
    else:
        nx.write_edgelist(subgraph, outfile, data=False)