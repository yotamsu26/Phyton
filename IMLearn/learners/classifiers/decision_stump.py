from __future__ import annotations
from typing import Tuple, NoReturn
from ...base import BaseEstimator
import numpy as np
from ...metrics import misclassification_error


class DecisionStump(BaseEstimator):
    """
    A decision stump classifier for {-1,1} labels according to the CART
     algorithm

    Attributes
    ----------
    self.threshold_ : float
        The threshold by which the data is split

    self.j_ : int
        The index of the feature by which to split the data

    self.sign_: int
        The label to predict for samples where the value of the j'th feature is
         about the threshold
    """

    def __init__(self) -> DecisionStump:
        """
        Instantiate a Decision stump classifier
        """
        super().__init__()
        self.threshold_, self.j_, self.sign_ = None, None, None

    def _fit(self, X: np.ndarray, y: np.ndarray) -> NoReturn:
        """
        fits a decision stump to the given data

        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features)
            Input data to fit an estimator for

        y : ndarray of shape (n_samples, )
            Responses of input data to fit to
        """
        best_error = float('inf')
        for j in range(len(X[0])):
            col_values = X[:, j]
            for sign in [-1, 1]:
                threshold_, err_ = \
                    self._find_threshold(col_values, y, sign)
                if err_ < best_error:
                    self.sign_, self.j_, self.threshold_ = sign, j, threshold_
                    best_error = err_

    def _predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict responses for given samples using fitted estimator

        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features)
            Input data to predict responses for

        Returns
        -------
        responses : ndarray of shape (n_samples, )
            Predicted responses of given samples

        Notes
        -----
        Feature values strictly below threshold are predicted as `-sign` whereas values which equal
        to or above the threshold are predicted as `sign`
        """
        pred = np.zeros(len(X))
        for i, sample in enumerate(X):
            if sample[self.j_] >= self.threshold_:
                pred[i] = self.sign_
            else:
                pred[i] = self.sign_ * -1
        return pred

    def _find_threshold(self, values: np.ndarray, labels: np.ndarray,
                        sign: int) -> Tuple[float, float]:
        """
        Given a feature vector and labels, find a threshold by which to
        perform a split The threshold is found according to the value
        minimizing the misclassification error along this feature

        Parameters
        ----------
        values: ndarray of shape (n_samples,)
            A feature vector to find a splitting threshold for

        labels: ndarray of shape (n_samples,)
            The labels to compare against

        sign: int
            Predicted label assigned to values equal to or above threshold

        Returns
        -------
        thr: float
            Threshold by which to perform split

        thr_err: float between 0 and 1
            Misclassificaiton error of returned threshold

        Notes
        -----
        For every tested threshold, values strictly below threshold are
        predicted as `-sign` whereas values which equal to or above the
        threshold are predicted as `sign`
        """
        # Sort values in ascending order
        sort_values = np.argsort(values)
        values, labels = values[sort_values], labels[sort_values]

        # loss for the minimize value
        loss = np.sum(np.abs(labels)[np.sign(labels) != sign])
        loss_arr = [loss]

        labels = labels * -sign
        loss_change = 0
        # update the loss according to change of every threshold
        for label in labels:
            loss_change += label
            loss_arr.append(loss - loss_change)

        # get the minimize
        index = np.argmin(loss_arr)
        values = np.concatenate([[-np.inf], values[1:], [np.inf]])
        return values[index], loss_arr[index]

    def _loss(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Evaluate performance under misclassification loss function

        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features)
            Test samples

        y : ndarray of shape (n_samples, )
            True labels of test samples

        Returns
        -------
        loss : float
            Performance under missclassification loss function
        """
        pred = self._predict(X)
        return misclassification_error(y, pred)
