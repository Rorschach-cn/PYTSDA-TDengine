import numpy as np
from sklearn.covariance import EllipticEnvelope
from pyodds.algo.base import Base

class RCOV(EllipticEnvelope,Base):
    '''
        An object for detecting outliers in a Gaussian distributed dataset.

    Parameters
    ----------
    store_precision : boolean, optional (default=True)
        Specify if the estimated precision is stored.
    assume_centered : boolean, optional (default=False)
        If True, the support of robust location and covariance estimates
        is computed, and a covariance estimate is recomputed from it,
        without centering the data.
        Useful to work with data whose mean is significantly equal to
        zero but is not exactly zero.
        If False, the robust location and covariance are directly computed
        with the FastMCD algorithm without additional treatment.
    support_fraction : float in (0., 1.), optional (default=None)
        The proportion of points to be included in the support of the raw
        MCD estimate. If None, the minimum value of support_fraction will
        be used within the algorithm: `[n_sample + n_features + 1] / 2`.
    contamination : float in (0., 0.5), optional (default=0.1)
        The amount of contamination of the data set, i.e. the proportion
        of outliers in the data set.
    random_state : int, RandomState instance or None, optional (default=None)
        The seed of the pseudo random number generator to use when shuffling
        the data.  If int, random_state is the seed used by the random number
        generator; If RandomState instance, random_state is the random number
        generator; If None, the random number generator is the RandomState
        instance used by `np.random`.

    Attributes
    ----------
    location_ : array-like, shape (n_features,)
        Estimated robust location
    covariance_ : array-like, shape (n_features, n_features)
        Estimated robust covariance matrix
    precision_ : array-like, shape (n_features, n_features)
        Estimated pseudo inverse matrix.
        (stored only if store_precision is True)
    support_ : array-like, shape (n_samples,)
        A mask of the observations that have been used to compute the
        robust estimates of location and shape.
    offset_ : float
        Offset used to define the decision function from the raw scores.
        We have the relation: ``decision_function = score_samples - offset_``.
        The offset depends on the contamination parameter and is defined in
        such a way we obtain the expected number of outliers (samples with
        decision function < 0) in training.
    Examples
    --------
    >>> import numpy as np
    >>> from sklearn.covariance import EllipticEnvelope
    >>> true_cov = np.array([[.8, .3],
    ...                      [.3, .4]])
    >>> X = np.random.RandomState(0).multivariate_normal(mean=[0, 0],
    ...                                                  cov=true_cov,
    ...                                                  size=500)
    >>> cov = EllipticEnvelope(random_state=0).fit(X)
    >>> # predict returns 1 for an inlier and -1 for an outlier
    >>> cov.predict([[0, 0],
    ...              [3, 3]])
    array([ 1, -1])
    >>> cov.covariance_ # doctest: +ELLIPSIS
    array([[0.7411..., 0.2535...],
           [0.2535..., 0.3053...]])
    >>> cov.location_
    array([0.0813... , 0.0427...])
    See Also
    --------
    EmpiricalCovariance, MinCovDet
    Notes
    -----
    Outlier detection from covariance estimation may break or not
    perform well in high-dimensional settings. In particular, one will
    always take care to work with ``n_samples > n_features ** 2``.
    References
    ----------
    .. [1] Rousseeuw, P.J., Van Driessen, K. "A fast algorithm for the
       minimum covariance determinant estimator" Technometrics 41(3), 212
       (1999)
    '''

    def anomaly_likelihood(self, X):
        """A normalization function to clip and scale the outlier_scores returned
        by self.decision_function(). Normalization is done separately for data
        points falling above and below the threshold
        Parameters
        ----------
        X : dataframe of shape (n_samples, n_features)
            The training input samples. Sparse matrices are accepted only
            if they are supported by the base estimator.
        Returns
        -------
        normalized_anomaly_scores : numpy array of shape (n_samples,)
            Normalized anomaly scores where 0.5 is the default threshold separating
            inliers with low scores from outliers with high score
        """
        outlier_score = self.decision_function(X)
        mask = outlier_score < 0

        sc_pos = outlier_score.clip(max=0)
        sc_neg = outlier_score.clip(min=0)

        lmn = np.copy(outlier_score)
        sc_pos = np.interp(sc_pos, (sc_pos.min(), sc_pos.max()), (1, 0.5))
        sc_neg = np.interp(sc_neg, (sc_neg.min(), sc_neg.max()), (0.5, 0.0))

        lmn[mask] = sc_pos[mask]
        lmn[np.logical_not(mask)] = sc_neg[np.logical_not(mask)]
        del outlier_score, sc_pos, sc_neg
        return lmn
