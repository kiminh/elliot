"""
Module description:

"""

__version__ = '0.1'
__author__ = 'Vito Walter Anelli, Claudio Pomo'
__email__ = 'vitowalter.anelli@poliba.it, claudio.pomo@poliba.it'

import os
from types import SimpleNamespace

from hyperopt import hp
from yaml import FullLoader as FullLoader
from yaml import load
from collections import OrderedDict
from utils.folder import manage_directories
import hyperoptimization as ho

_experiment = 'experiment'
_dataset = 'dataset'
_weights = 'path_output_rec_weight'
_performance = 'path_output_rec_performance'
_verbose = 'verbose'
_recs = 'path_output_rec_result'
_top_k = 'top_k'
_metrics = 'metrics'
_relevance = 'relevance'
_models = 'models'
_recommender = 'recommender'
_gpu = 'gpu'
_hyper_max_evals = 'hyper_max_evals'
_hyper_opt_alg = 'hyper_opt_alg'
_data_paths = 'data_paths'


class NameSpaceModel:
    def __init__(self, config_path):
        self.base_namespace = SimpleNamespace()

        self.config_file = open(config_path)
        self.config = load(self.config_file, Loader=FullLoader)

        os.environ['CUDA_VISIBLE_DEVICES'] = str(self.config[_experiment][_gpu])

    def fill_base(self):

        for path in self.config[_experiment][_data_paths].keys():
            self.config[_experiment][_data_paths][path] = \
                self.config[_experiment][_data_paths][path].format(self.config[_experiment][_dataset])

        self.config[_experiment][_recs] = self.config[_experiment][_recs] \
            .format(self.config[_experiment][_dataset])
        self.config[_experiment][_weights] = self.config[_experiment][_weights] \
            .format(self.config[_experiment][_dataset])
        self.config[_experiment][_performance] = self.config[_experiment][_performance] \
            .format(self.config[_experiment][_dataset])

        manage_directories(self.config[_experiment][_recs], self.config[_experiment][_weights],
                           self.config[_experiment][_performance])

        for p in [_data_paths, _weights, _recs, _dataset, _top_k, _metrics, _relevance, _performance]:
            if p == _data_paths:
                setattr(self.base_namespace, p, SimpleNamespace(**self.config[_experiment][p]))
            else:
                setattr(self.base_namespace, p, self.config[_experiment][p])

    def fill_model(self):
        for key in self.config[_experiment][_models]:
            if any(isinstance(value, list) for value in self.config[_experiment][_models][key].values()):
                space_list = []
                for k, value in self.config[_experiment][_models][key].items():
                    if isinstance(value, list):
                        space_list.append((k, hp.choice(k, value)))
                _SPACE = OrderedDict(space_list)
                _max_evals = self.config[_experiment][_models][key][_hyper_max_evals]
                _opt_alg = ho.parse_algorithms(self.config[_experiment][_models][key][_hyper_opt_alg])
                yield key, (SimpleNamespace(**self.config[_experiment][_models][key]), _SPACE, _max_evals, _opt_alg)
            else:
                yield key, SimpleNamespace(**self.config[_experiment][_models][key])