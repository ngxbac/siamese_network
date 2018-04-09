import torch

class Configure(object):
    def __init__(self):
        super(Configure, self).__init__()
        self.dataroot = "../../input/dlib_gen"
        self.n_cls = 17
        self.n_same = 7
        self.n_batch = 20 # Number of training example: n_batch * n_cls * n_same
        self.lr = 0.1
        self.lr_decay = 1e-4
        self.wd = 0
        self.optimizer = 'adagrad'
        self.resume = None
        self.start_epoch = 0
        self.epochs = 5
        self.cuda = torch.cuda.is_available()