from __future__ import print_function, unicode_literals
import numpy
from preshed.maps import PreshMap

try:
    import cupy
    from cupy import get_array_module
except ImportError:
    cupy = None
    get_array_module = lambda _: numpy

try:
    basestring
except NameError:
    basestring = str

try:
    unicode
except NameError:
    unicode = str


from pathlib import Path


def is_cupy_array(arr):
    '''Check whether an array is a cupy array'''
    if cupy is None:
        return False
    elif isinstance(arr, cupy.ndarray):
        return True
    else:
        return False

def is_numpy_array(arr):
    '''Check whether an array is a numpy array'''
    if isinstance(arr, numpy.ndarray):
        return True
    else:
        return False

def get_ops(ops):
    from .ops import NumpyOps, CupyOps
    if ops in ('numpy', 'cpu') or (isinstance(ops, int) and ops < 0):
        return NumpyOps
    elif ops in ('cupy', 'gpu') or (isinstance(ops, int) and ops >= 0):
        return CupyOps
    else:
        raise ValueError("Invalid ops (or device) description: %s" % ops)

def prefer_gpu():
    '''Use GPU if it's available. Returns True if so, False otherwise.'''
    from ._classes.model import Model
    from .ops import CupyOps
    if CupyOps.xp is not None:
        Model.Ops = CupyOps
        Model.ops = CupyOps()
        return True
    else:
        return False

def require_gpu():
    from ._classes.model import Model
    from .ops import CupyOps
    if CupyOps.xp is not None:
        raise ValueError("GPU is not accessible. Was the library installed correctly?")
    Model.Ops = CupyOps
    Model.ops = CupyOps()
    return True


def mark_sentence_boundaries(sequences, drop=0.): # pragma: no cover
    '''Pad sentence sequences with EOL markers.'''
    for sequence in sequences:
        sequence.insert(0, '-EOL-')
        sequence.insert(0, '-EOL-')
        sequence.append('-EOL-')
        sequence.append('-EOL-')
    return sequences, None


def add_eos_bos(sentences):
    '''Add eos and bos tokens to a batch of sentences'''
    for sentence in sentences:
        sentence.insert(0, '<bos>')
        sentence.append('<eos>')
    return sentences

def remap_ids(ops):
    id_map = {0: 0}
    def begin_update(ids, drop=0.):
        n_vector = len(id_map)
        for i, id_ in enumerate(ids):
            if id_ not in id_map:
                id_map[id_] = n_vector
                n_vector += 1
            ids[i] = id_map[id_]
        return ids, None
    return begin_update

def copy_array(dst, src, casting='same_kind', where=None):
    if isinstance(dst, numpy.ndarray) and isinstance(src, numpy.ndarray):
        dst[:] = src
    elif isinstance(dst, cupy.ndarray):
        src = cupy.array(src, copy=False)
        cupy.copyto(dst, src)
    else:
        numpy.copyto(dst, src)

def ensure_path(path):
    if isinstance(path, unicode) or isinstance(path, str):
        return Path(path)
    else:
        return path

def to_categorical(y, nb_classes=None):
    # From keras
    xp = get_array_module(y)
    if xp is cupy:
        y = y.get()
    y = numpy.array(y, dtype='int').ravel()
    if not nb_classes:
        nb_classes = numpy.max(y) + 1
    n = y.shape[0]
    categorical = numpy.zeros((n, nb_classes), dtype='float32')
    categorical[numpy.arange(n), y] = 1
    return xp.asarray(categorical)


def flatten_sequences(sequences, drop=0.): # pragma: no cover
    xp = get_array_module(sequences[0])
    return xp.concatenate(sequences), None


def partition(examples, split_size): # pragma: no cover
    examples = list(examples)
    numpy.random.shuffle(examples)
    n_docs = len(examples)
    split = int(n_docs * split_size)
    return examples[:split], examples[split:]


def minibatch(stream, batch_size=1000): # pragma: no cover
    if hasattr(stream, '__len__') and hasattr(stream, '__getitem__'):
        i = 0
        while i < len(stream):
            yield stream[i : i + batch_size]
            i += batch_size
    else:
        batch = []
        for X in stream:
            batch.append(X)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if len(batch) != 0:
            yield batch


def numericalize(nlp):
    ''' Numericalize vocabulary in a continuous range '''
    word2indx = {}
    indx2word = {}
    for indx, word in enumerate(nlp.vocab):
        word2indx[word] = indx
        indx2word[indx] = word
    word2indx['oov'] = len(nlp.vocab)
    indx2word[len(nlp.vocab)] = 'oov'
    return word2indx, indx2word
