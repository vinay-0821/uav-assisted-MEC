import numpy as np

class TerminalDevice:
    def __init__(self, id, position, params):
        self.id = id
        self.position = np.array(position)
        self.params = params
        self.fm = 0  
        self.energy_local = 0
        self.energy_offload = 0

    def distance_to(self, pos_uav):
        return np.linalg.norm(pos_uav - self.position)

    def channel_gain(self, pos_uav):
        alpha0 = self.params['alpha0']
        H1 = self.params['H1']
        d = np.sqrt(np.sum((pos_uav[:2] - self.position[:2]) ** 2) + H1 ** 2)
        return alpha0 / (d ** 2)

    def compute_local_energy(self, fm):
        kappa_m = self.params['kappa_m']
        delta = self.params['total_time'] / self.params['num_slots']
        energy = delta * kappa_m * (fm ** 3)
        self.energy_local += energy
        return energy

class UAV:
    def __init__(self, id, position, params):
        self.id = id
        self.position = np.array(position)
        self.params = params
        self.energy_fly = 0
        self.energy_compute = 0

    def fly_energy(self, v):
        eps1 = self.params['epsilon1']
        eps2 = self.params['epsilon2']
        delta = self.params['total_time'] / self.params['num_slots']
        return delta * (eps1 * (v ** 3) + eps2 * v)

    def channel_gain_to(self, pos_other):
        alpha0 = self.params['alpha0']
        H1, H2 = self.params['H1'], self.params['H2']
        d = np.sqrt(np.sum((self.position[:2] - pos_other[:2]) ** 2) + (H1 - H2) ** 2)
        return alpha0 / (d ** 2)
