# Glossary

Use this page to record terms and ideas that help you understand
professional analytics projects.

This project covers ensemble methods: combining multiple models
to produce better predictions than any single model alone.

Pro-tip: Expand the VS Code **Outline** view (below the navigator on the right)
to see this file organization at-a-glance.

## Ensemble Methods

### ensemble method

An ensemble method combines the predictions of multiple models
to produce a single, more reliable result.
Ensembles often outperform any individual model because different models
make different errors, and combining them averages those errors out.

### bagging

Bagging (bootstrap aggregating) trains many models independently
on different random samples of the training data
and combines their predictions by majority vote or averaging.
Random forests use bagging.

### boosting

Boosting trains models sequentially, where each new model focuses on
the examples the previous ones got wrong.
The final prediction combines all models weighted by their accuracy.
Gradient boosting uses this approach.

### random forest

A random forest is an ensemble of decision trees trained on random
subsets of the data and random subsets of the features.
Predictions are made by majority vote across all trees.
Random forests are robust, accurate, and resistant to overfitting.

### gradient boosting

Gradient boosting builds trees sequentially, each one correcting
the residual errors of the previous.
It often achieves high accuracy but requires careful tuning
to avoid overfitting.

### feature importance

Feature importance is a score that measures how much each input feature
contributed to a model's predictions.
Tree-based models compute this automatically.
High importance means the feature was used frequently and effectively
to split the data.

## Tuning

### hyperparameter

A hyperparameter is a setting that controls how a model is trained,
set before training begins.
Examples include the number of trees in a forest,
the maximum depth of each tree, and the learning rate.
Choosing good hyperparameters improves model performance.

### n_estimators

`n_estimators` is the hyperparameter that controls how many trees
are built in a random forest or gradient boosting model.
More trees generally improve accuracy up to a point,
after which returns diminish and training slows.

### max_depth

`max_depth` controls how deep each decision tree is allowed to grow.
Shallow trees underfit; very deep trees overfit.
The right depth depends on the data.

### cross-validation

Cross-validation evaluates a model by splitting the data into multiple
folds, training on some and testing on others, and averaging the results.
It gives a more reliable estimate of performance than a single train-test split.

### bias-variance tradeoff

The bias-variance tradeoff describes the tension between two types of error.
High bias means the model is too simple and misses patterns (underfitting).
High variance means the model is too complex and fits noise (overfitting).
Ensembles reduce variance while keeping bias low.
