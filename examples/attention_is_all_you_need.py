from thinc.neural.ops import NumpyOps, CupyOps, Ops
from thinc.neural.optimizers import initNoAm
from thinc.v2v import Model
import plac
import spacy
from thinc.extra.datasets import get_iwslt


class ModelException(Exception):
    pass

class BatchesException(Exception):
    pass

@plac.annotations(
    heads=("number of heads of the multiheaded attention", "option"),
    dropout=("model dropout", "option")
)
def main(heads=6, dropout=0.1):
    if (CupyOps.xp != None):
        Model.ops = CupyOps()
        Model.Ops = CupyOps
        print('Training on GPU')
    else:
        print('Training on CPU')
    train, dev, test = get_iwslt()
    train_X, train_Y = zip(*train)
    dev_X, dev_Y = zip(*dev)
    test_X, test_Y = zip(*test)
    tokenizer = lambda x: spacy.load('en_core_web_sm').tokenizer(x)
    vectorizer = spacy.load('en_vectors_web_lg')
    raise BatchesException('Batchify not implemented yet.')
    raise ModelException('Model not composed yet.')
    with model.begin_training(train_X, train_Y, optimizer=initNoAm(input_size)) \
            as (trainer, optimizer):
            raise NotImplementedError




if __name__ == '__main__':
    plac.call(main)
