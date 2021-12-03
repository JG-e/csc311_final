from starter_code.utils import *

import numpy as np
import matplotlib.pyplot as plt


def sigmoid(x):
    """ Apply sigmoid function.
    """
    return np.exp(x) / (1 + np.exp(x))


def neg_log_likelihood(data, theta, beta, randomness, slopes):
    """ Compute the negative log-likelihood.

    You may optionally replace the function arguments to receive a matrix.

    :param data: A dictionary {user_id: list, question_id: list,
    is_correct: list}
    :param theta: Vector
    :param beta: Vector
    :return: float
    """
    #####################################################################
    # wasTODO:                                                             #
    # Implement the function as described in the docstring.             #
    #####################################################################
    log_lklihood = 0.
    for i in range(len(data["user_id"])):
        diff = theta[data["user_id"][i]] - beta[data["question_id"][i]]
        log_lklihood += data["is_correct"][i] * diff - np.log1p(np.exp(diff))
    #####################################################################
    #                       END OF YOUR CODE                            #
    #####################################################################
    return -log_lklihood


def update_theta_beta(data, lr, theta, beta, randomness, slopes):
    """ Update theta and beta using gradient descent.

    You are using alternating gradient descent. Your update should look:
    for i in iterations ...
        theta <- new_theta
        beta <- new_beta

    You may optionally replace the function arguments to receive a matrix.

    :param data: A dictionary {user_id: list, question_id: list,
    is_correct: list}
    :param lr: float
    :param theta: Vector
    :param beta: Vector
    :return: tuple of vectors
    """
    #####################################################################
    # wasTODO:                                                             #
    # Implement the function as described in the docstring.             #
    #####################################################################

    theta_copy = theta.copy()
    beta_copy = beta.copy()
    randomness_copy = randomness.copy()
    slopes_copy = slopes.copy()

    for i in range(len(data["user_id"])):

        c = data["is_correct"][i]
        k = slopes_copy[data["question_id"][i]]
        a = randomness_copy[data["question_id"][i]]
        x = theta_copy[data["user_id"][i]]
        y = beta_copy[data["question_id"][i]]
        theta[data["user_id"][i]] += lr * (k * np.exp(x)*((c-1)*k*np.exp(x) + (c - a) * np.exp(y)))/(k * np.exp(x) + np.exp(y)) / (k * np.exp(x) + a*np.exp(y))
        beta[data["question_id"][i]] += - lr * (k*np.exp(x)*((c-a)*np.exp(y)+(c-1)*k*np.exp(x)))/(k * np.exp(x) + np.exp(y)) / (k * np.exp(x) + a*np.exp(y))
        slopes[data["question_id"][i]] += 0.1 * lr * (np.exp(y)*a - c*np.exp(y) + (1-c)*k*np.exp(x))/(a-1)/(np.exp(y)*a+k*np.exp(x))
        randomness[data["question_id"][i]] += 0.05 * lr * np.exp(x)*((c-1)*k*np.exp(x)+(c-a)*np.exp(y))/(np.exp(x)*k+np.exp(y))/(np.exp(x)*k+a*np.exp(y))
    for i in range(len(data["user_id"])):
        if randomness[data["question_id"][i]] < 0:
            randomness[data["question_id"][i]] = 0
        if randomness[data["question_id"][i]] >= 1:
            randomness[data["question_id"][i]] = 0.9999

    #####################################################################
    #                       END OF YOUR CODE                            #
    #####################################################################
    return theta, beta, randomness, slopes


def irt(data, val_data, test_data, lr, iterations, quiet=False):
    """ Train IRT model.

    You may optionally replace the function arguments to receive a matrix.

    :param data: A dictionary {user_id: list, question_id: list,
    is_correct: list}
    :param val_data: A dictionary {user_id: list, question_id: list,
    is_correct: list}
    :param lr: float
    :param iterations: int
    :param quiet: bool
    :return: (theta, beta, val_acc_lst)
    """
    # wasTODO: Initialize theta and beta.
    theta = np.ones(542) * 0.1
    beta = np.ones(1774) * 0.1
    randomness = np.ones(1774) * 0.0
    slopes= np.ones(1774) * 1.0

    validation_log_likelihood = []
    train_log_likelihood = []

    for i in range(iterations):
        train_neg_lld = neg_log_likelihood(data, theta=theta, beta=beta, randomness=randomness, slopes=slopes)
        train_log_likelihood.append(train_neg_lld)
        validation_neg_lld = neg_log_likelihood(val_data, theta=theta,
                                                beta=beta, randomness=randomness, slopes=slopes)
        validation_log_likelihood.append(validation_neg_lld)
        score_train = evaluate(data=data, theta=theta, beta=beta, randomness=randomness, slopes=slopes)
        score_validation = evaluate(data=val_data, theta=theta, beta=beta, randomness=randomness, slopes=slopes)
        score_test = evaluate(data=test_data, theta=theta, beta=beta, randomness=randomness, slopes=slopes)
        # val_acc_lst.append(score_train)
        if not quiet:
            print("Iterations: {} \t NLLK: {} \t Train Score: {} \t Validation Score: {} \t Test Score: {}".format(
                i+1, train_neg_lld, score_train, score_validation, score_test))
        theta, beta, randomness, slopes = update_theta_beta(data, lr, theta, beta, randomness, slopes)

    # wasTODO: You may change the return values to achieve what you want.
    return theta, beta, randomness, slopes, validation_log_likelihood, train_log_likelihood


def evaluate(data, theta, beta, randomness, slopes):
    """ Evaluate the model given data and return the accuracy.
    :param data: A dictionary {user_id: list, question_id: list,
    is_correct: list}

    :param theta: Vector
    :param beta: Vector
    :return: float
    """
    pred = []
    for i, q in enumerate(data["question_id"]):
        u = data["user_id"][i]
        k = slopes[data["question_id"][i]]
        a = randomness[data["question_id"][i]]
        x = (theta[u] - beta[q]).sum() * k
        p_a = sigmoid(x) * (1-a) + a
        pred.append(p_a >= 0.5)
    return np.sum((data["is_correct"] == np.array(pred))) \
           / len(data["is_correct"])


def main():
    train_data = load_train_csv("../data")
    # You may optionally use the sparse matrix.
    # sparse_matrix = load_train_sparse("../data")
    val_data = load_valid_csv("../data")
    test_data = load_public_test_csv("../data")

    #####################################################################
    # wasTODO:                                                             #
    # Tune learning rate and number of iterations. With the implemented #
    # code, report the validation and test accuracy.                    #
    #####################################################################
    lr = 0.015
    iterations = 50
    theta, beta, randomness, slopes, validation_log_likelihood, training_log_likelihood = irt(
        train_data, val_data, test_data, lr, iterations)

    #plt.title("validation log likelihood")
    #plt.xlabel("iteration")
    #plt.ylabel("validation log likelihood")
    #plt.plot(range(iterations), validation_log_likelihood)
    #plt.show()

    #plt.title("training log likelihood")
    #plt.xlabel("iteration")
    #plt.ylabel("training log likelihood")
    #plt.plot(range(iterations), training_log_likelihood)
    #plt.show()

    #acc_test = evaluate(test_data, theta, beta, randomness, slopes)
    #print("Test Score: {}".format(acc_test))
    #####################################################################
    #                       END OF YOUR CODE                            #
    #####################################################################

    #####################################################################
    # wasTODO:                                                             #
    # Implement part (d)                                                #
    #####################################################################
    #questions = np.array([150, 300, 450])
    #theta = theta.reshape(-1)
    #theta.sort()
    #for question in questions:
    #    e = np.exp(theta - beta[question])
    #    plt.plot(theta, e / (1 + e), label="Question {}".format(question))
    #plt.ylabel("Probability")
    #plt.xlabel("Theta")
    #plt.title("Probablity to theta")
    #plt.legend()
    #plt.show()

    #####################################################################
    #                       END OF YOUR CODE                            #
    #####################################################################


if __name__ == "__main__":
    main()
