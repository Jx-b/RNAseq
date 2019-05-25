# utils for RNAseq
import json
from time import sleep

import numpy as np
import requests

from sklearn.decomposition import PCA
from scipy.stats.mstats import zscore


ENRICHR_URL = 'http://amp.pharm.mssm.edu/Enrichr'

def _enrichr_add_list(genes, meta=''):
	"""POST a gene list to Enrichr server and return the list ids"""
	genes_str = '\n'.join(genes)
	payload = {
		'list': (None, genes_str),
		'description': (None, meta)
	}
	# POST genes to the /addList endpoint
	response = requests.post("%s/addList" % ENRICHR_URL, files=payload)
	list_ids = json.loads(response.text)
	return list_ids


def enrichr_link(genes, meta=''):
	"""POST a gene list to Enrichr server and get the link."""
	list_ids = _enrichr_add_list(genes, meta)
	shortId = list_ids['shortId']
	link = '%s/enrich?dataset=%s' % (ENRICHR_URL, shortId)
	return link


def enrichr_result(genes, meta='', gmt=''):
	"""POST the genes to Enrichr and return the enrichment results 
	for a specific gene-set library on Enrichr"""
	list_ids = _enrichr_add_list(genes, meta)
	# GET from the /export endpoint
	query_string = '?userListId=%s&backgroundType=%s' % \
		(list_ids['userListId'], gmt)

	url = '%s/enrich%s' % (ENRICHR_URL, query_string)
	sleep(2)

	response = requests.get(url)
	if response.status_code == 200:
		results = json.loads(response.text)
		return results
	else:
		raise Exception('HTTP reponse code=%s' % response.status_code)


def enrichr_term_score(genes, meta='', gmt=''):
	"""Use Enrichr API to only get terms and scores"""
	results = enrichr_result(genes, meta=meta, gmt=gmt)[gmt]
	terms_scores = []
	for res in results:
		term = res[1]
		combined_score = res[4]
		terms_scores.append((term, combined_score))
	return terms_scores


def perform_PCA(fpkmMatrix, standardize=3, log=True):
	## preprocessing of the fpkmMatrix
	if log:
		fpkmMatrix = np.log10(fpkmMatrix + 1.)
	if standardize == 2: # standardize along rows/genes
		fpkmMatrix = zscore(fpkmMatrix, axis=1)
	elif standardize == 1: # standardize along cols/samples
		fpkmMatrix = zscore(fpkmMatrix, axis=0)

	## remove genes with NaNs
	fpkmMatrix = fpkmMatrix[~np.isnan(np.sum(fpkmMatrix, axis=1))]

	pca = PCA(n_components=None)
	## get variance captured
	pca.fit(fpkmMatrix.T)
	variance_explained = pca.explained_variance_ratio_[0:3]
	variance_explained *= 100
	## compute PCA and plot
	pca_transformed = pca.transform(fpkmMatrix.T)
	return variance_explained, pca_transformed