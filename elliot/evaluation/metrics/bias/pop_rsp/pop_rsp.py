"""
This is the implementation of the Popularity-based Ranking-based Statistical Parity (RSP) metric.
It proceeds from a user-wise computation, and average the values over the users.
"""

__version__ = '0.1'
__author__ = 'Vito Walter Anelli, Claudio Pomo'
__email__ = 'vitowalter.anelli@poliba.it, claudio.pomo@poliba.it'

import operator

import numpy as np
from elliot.evaluation.metrics.base_metric import BaseMetric


class PopRSP(BaseMetric):
    r"""
    This class represents the implementation of the Popularity-based Ranking-based Statistical Parity (RSP) recommendation metric.
    Passing 'PopRSP' to the metrics list will enable the computation of the metric.


     .. _PopRSP:   "Measuring and Mitigating Item Under-Recommendation Bias in Personalized Ranking Systems."
    Zhu, Ziwei, Jianling Wang, and James Caverlee.
    Proceedings of the 43rd International ACM SIGIR
    Conference on Research and Development in Information Retrieval. 2020.

     .. math::
        \mathrm {RSP}=\frac{{std}\left(P\left(R @ k \mid g=g_{1}\right), \ldots, P\left(R @ k \mid g=g_{A}\right)\right)}
        {{mean}\left(P\left(R @ k \mid g=g_{1}\right), \ldots, P\left(R @ k \mid g=g_{A}\right)\right)}

    :math:`P\left(R @ k \mid g=g_{a}\right)}` is `\frac{\sum_{u=1}^{N} \sum_{i=1}^{k} G_{g_{a}}\left(R_{u, i}\right)}
    {\sum_{u=1}^{N} \sum_{i \in I \backslash I_{u}^{+}} G_{g_{a}}(i)}`

    :math:`\sum_{i=1}^{k} G_{g_{a}}\left(R_{u, i}\right)` calculates how many un-interacted items
    from group `{g_a}` are ranked in top-𝑘 for user u.

    :math:`\sum_{i \in I \backslash I_{u}^{+}} G_{g_{a}}(i)`
    calculates how many un-interacted items belong to group `{g_a}` for u
    """

    def __init__(self, recommendations, config, params, eval_objects):
        """
        Constructor
        :param recommendations: list of recommendations in the form {user: [(item1,value1),...]}
        :param config: SimpleNameSpace that represents the configuration of the experiment
        :param params: Parameters of the model
        :param eval_objects: list of objects that may be useful for the computation of the different metrics
        """
        super().__init__(recommendations, config, params, eval_objects)
        self._cutoff = self._evaluation_objects.cutoff
        self._short_head = set(self._evaluation_objects.pop.get_short_head())
        self._long_tail = set(self._evaluation_objects.pop.get_long_tail())
        self._train = self._evaluation_objects.data.train_dict
        self._num = []
        self._den = []

    @staticmethod
    def name():
        """
        Metric Name Getter
        :return: returns the public name of the metric
        """
        return "PopRSP"

    def __user_pop_rsp(self, user_recommendations, cutoff, long_tail, short_head, u_train):
        """
        Per User Popularity-based Ranking-based Statistical Parity (RSP)
        :param user_recommendations: list of user recommendation in the form [(item1,value1),...]
        :param cutoff: numerical threshold to limit the recommendation list
        :param user_relevant_items: list of user relevant items in the form [item1,...]
        :return: the value of the Average Recommendation Popularity metric for the specific user
        """
        recommended_items = set([i for i, _ in user_recommendations[:cutoff]])
        num_h = len(recommended_items & short_head)
        num_t = len(recommended_items & long_tail)
        den_h = len(short_head-u_train)
        den_t = len(long_tail-u_train)
        return num_h, num_t, den_h, den_t

    def eval(self):
        """
        Evaluation function
        :return: the overall averaged value of PopRSP
        """
        for u, u_r in self._recommendations.items():
            num_h, num_t, den_h, den_t = self.__user_pop_rsp(u_r, self._cutoff, self._long_tail, self._short_head, set(self._train[u].keys()))
            self._num.append([num_h, num_t])
            self._den.append([den_h, den_t])
        self._num = np.sum(np.array(self._num), axis = 0)
        self._den = np.sum(np.array(self._den), axis = 0)
        pr = self._num / self._den
        return np.std(pr)/np.mean(pr)

