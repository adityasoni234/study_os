"""Passage texts for the demo notebook's SourceChunk rows (used by core.py, which maps
each key to a source and page). No seed() here on purpose — this module is data only."""

PASSAGES: dict[str, str] = {
    "unit3-p14": (
        "Precision and recall are the two workhorse metrics for classification. "
        "Precision = TP / (TP + FP): of everything the model flagged as positive, the "
        "fraction that really was positive. Recall = TP / (TP + FN): of everything that "
        "actually was positive, the fraction the model caught. Precision punishes false "
        "alarms while recall punishes misses, so improving one usually trades off against "
        "the other."
    ),
    "unit3-p15": (
        "The F1 score folds precision and recall into a single number using the harmonic "
        "mean: F1 = 2 x (precision x recall) / (precision + recall). The harmonic mean is "
        "deliberately pessimistic — it sits close to the smaller of the two values, so a "
        "model cannot hide terrible recall behind perfect precision. F1 reaches 1 only "
        "when precision and recall are both 1, and it collapses toward 0 if either one does."
    ),
    "unit3-p18": (
        "A ROC curve plots the true positive rate (recall) against the false positive rate "
        "as the decision threshold sweeps from strict to lenient. A perfect classifier "
        "hugs the top-left corner, while a random one tracks the diagonal. The area under "
        "the curve (AUC) summarises the whole curve: it equals the probability that a "
        "randomly chosen positive example is ranked above a randomly chosen negative one."
    ),
    "unit3-p22": (
        "Gradient descent minimises a loss function by repeatedly stepping opposite to the "
        "gradient: theta <- theta - alpha * grad J(theta). The learning rate alpha sets the "
        "step size — too small and training crawls, too large and the loss oscillates or "
        "diverges. Stochastic and mini-batch variants estimate the gradient from a subset "
        "of the data, accepting noisier steps in exchange for much cheaper iterations."
    ),
    "unit3-p31": (
        "Overfitting is when a model memorises its training data, noise included, and stops "
        "generalising: training accuracy stays high while test accuracy falls away. It is "
        "the high-variance end of the bias-variance trade-off. Standard remedies are more "
        "data, regularisation (L1/L2, dropout), a simpler model, or early stopping — and it "
        "is diagnosed with a held-out validation set or cross-validation, never the "
        "training set."
    ),
    "statquest": (
        "So imagine we trained a model to decide whether an email is spam. Precision asks: "
        "of all the emails we called spam, what fraction really were spam — that is TP "
        "divided by TP plus FP. Recall asks a different question: of all the spam that "
        "actually showed up, what fraction did we catch — TP divided by TP plus FN. Bam! "
        "And notice you could get perfect recall just by calling everything spam, but your "
        "precision would be awful — which is exactly why we always look at both together."
    ),
}
