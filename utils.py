import torch
from torch.autograd import Variable,Function

class PairwiseDistance(Function):
    def __init__(self, p):
        super(PairwiseDistance, self).__init__()
        self.norm = p

    def forward(self, x, y=None):
        '''
        Input: x is a Nxd matrix
               y is an optional Mxd matirx
        Output: dist is a NxM matrix where dist[i,j] is the square norm between x[i,:] and y[j,:]
                if y is not given then use 'y=x'.
        i.e. dist[i,j] = ||x[i,:]-y[j,:]||^2
        '''
        x_norm = (x ** 2).sum(1).view(-1, 1)
        if y is not None:
            y_norm = (y ** 2).sum(1).view(1, -1)
        else:
            y = x
            y_norm = x_norm.view(1, -1)

        dist = x_norm + y_norm - 2.0 * torch.mm(x, torch.transpose(y, 0, 1))
        return dist

class DlibLoss(Function):
    """Triplet loss function.
    """
    def __init__(self, margin=0.04, dis_th=0.6):
        super(DlibLoss, self).__init__()
        self.margin = margin
        self.dis_th = dis_th
        self.pdist = PairwiseDistance(2)  # norm 2

    def forward(self, feature1, feature2, label):
        loss = Variable(torch.FloatTensor([0]))
        distance = self.pdist.forward(feature1, feature2).sqrt()
        num_pos_samps = 0.00001
        for i in range(distance.shape[0]):
            for j in range(distance.shape[0]):
                if i == j:
                    continue
                if torch.equal(label[i], label[j]):
                    num_pos_samps += 1
                    loss += torch.max(Variable(torch.FloatTensor([0])), distance[i][j].cpu() - Variable(torch.FloatTensor([self.dis_th + self.margin])))
                else:
                    loss += torch.max(Variable(torch.FloatTensor([0])), Variable(torch.FloatTensor([self.dis_th + self.margin])) - distance[i][j].cpu())

        return loss * 0.5 / num_pos_samps

class ContrastiveLoss(torch.nn.Module):
    """
    Contrastive loss function.
    Based on:
    """

    def __init__(self, margin=1.0):
        super(ContrastiveLoss, self).__init__()
        self.margin = margin
        self.pdist = PairwiseDistance(2)  # norm 2

    def forward(self, feature1, feature2, label):
        
        loss = Variable(torch.FloatTensor([0]))
        distance = self.pdist.forward(feature1, feature2)
        count = 0
        for i in range(distance.shape[0]):
            for j in range(distance.shape[0]):
                if i == j:
                    continue
                mdist = Variable(torch.FloatTensor([self.margin])) - distance[i][j].sqrt().cpu()
                dist = torch.clamp(mdist, min=0.0)
                y = label[i] == label[j]
                loss += y.type(torch.FloatTensor).cpu() * distance[i][j].cpu() + (1-y.type(torch.FloatTensor).cpu()) * torch.pow(distance[i][j].sqrt().cpu(), 2)
                count += 1

        return loss / 2.0 / count