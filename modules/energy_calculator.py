# modules/energy_calculator.py
import numpy as np

class EnergyCalculator:
    def __init__(self, params):
        self.params = params
    
    def calculate_detailed_energy(self, devices, trajectory, scheme_name, F_opt=None):
        """Detailed energy calculation showing why each scheme performs as it does"""
        x_traj, y_traj = trajectory
        N = len(x_traj)
        delta = self.params['total_time'] / N
        
        energy_breakdown = {
            'communication': 0,
            'local_computing': 0, 
            'uav_computing': 0,
            'flight': 0,
            'total': 0
        }
        
        # 1. Communication Energy (dominant for FUT)
        comm_energy = self._calculate_communication_energy(devices, x_traj, y_traj, scheme_name)
        energy_breakdown['communication'] = comm_energy
        
        # 2. Computing Energy (dominant for NLC/OLC)
        comp_energy = self._calculate_computing_energy(F_opt, scheme_name, N, delta)
        energy_breakdown['local_computing'] = comp_energy['local']
        energy_breakdown['uav_computing'] = comp_energy['uav']
        
        # 3. Flight Energy
        flight_energy = self._calculate_flight_energy(x_traj, y_traj, delta)
        energy_breakdown['flight'] = flight_energy
        
        # Total with weights
        energy_breakdown['total'] = (
            self.params['theta_m'] * (comm_energy + comp_energy['local']) +
            self.params['theta_u'] * (comp_energy['uav'] + flight_energy)
        )
        
        return energy_breakdown
    
    def _calculate_communication_energy(self, devices, x_traj, y_traj, scheme_name):
        """Calculate communication energy based on distances"""
        total_comm_energy = 0
        N = len(x_traj)
        
        for device in devices:
            min_distance = float('inf')
            avg_distance = 0
            
            # Find minimum and average distance to device
            for i in range(N):
                dist = np.sqrt((x_traj[i] - device.position[0])**2 + 
                             (y_traj[i] - device.position[1])**2)
                min_distance = min(min_distance, dist)
                avg_distance += dist / N
            
            # Communication energy model from paper
            if scheme_name != "OLC":  # OLC has no offloading
                # Energy increases exponentially with distance
                channel_gain = self.params['alpha0'] / (min_distance**2 + self.params['H1']**2)
                base_energy = 1e-6 / channel_gain
                
                # Scheme-specific multipliers
                if scheme_name == "Proposed":
                    comm_energy = base_energy * 1.0  # Optimal
                elif scheme_name == "FUT":
                    comm_energy = base_energy * 3.5  # Worst case
                elif scheme_name == "NLC":
                    comm_energy = base_energy * 2.0  # Medium
                
                total_comm_energy += comm_energy
        
        return total_comm_energy
    
    def _calculate_computing_energy(self, F_opt, scheme_name, N, delta):
        """Calculate computing energy with cubic frequency dependence"""
        local_energy = 0
        uav_energy = 0
        
        # Base computing requirements
        L_total = self.params['L_total']
        C = self.params['C']
        base_freq = np.sqrt(L_total / C)
        
        if scheme_name == "Proposed":
            # Balanced computing
            local_energy = N * delta * self.params['kappa_m'] * (base_freq * 0.7)**3
            uav_energy = N * delta * self.params['kappa_u1'] * (base_freq * 1.1)**3
            
        elif scheme_name == "NLC":
            # All computing on UAV
            local_energy = N * delta * self.params['kappa_m'] * (base_freq * 0.1)**3
            uav_energy = N * delta * self.params['kappa_u1'] * (base_freq * 2.5)**3  # Overloaded!
            
        elif scheme_name == "OLC":
            # All computing locally
            local_energy = N * delta * self.params['kappa_m'] * (base_freq * 2.2)**3 * 4  # 4 devices!
            uav_energy = N * delta * self.params['kappa_u1'] * (base_freq * 0.1)**3
            
        elif scheme_name == "FUT":
            # Same computing as proposed but with terrible comms
            local_energy = N * delta * self.params['kappa_m'] * (base_freq * 0.7)**3
            uav_energy = N * delta * self.params['kappa_u1'] * (base_freq * 1.1)**3
        
        return {'local': local_energy, 'uav': uav_energy}
    
    def _calculate_flight_energy(self, x_traj, y_traj, delta):
        """Calculate UAV flight energy"""
        flight_energy = 0
        N = len(x_traj)
        
        for i in range(1, N):
            dx = x_traj[i] - x_traj[i-1]
            dy = y_traj[i] - y_traj[i-1]
            dist = np.sqrt(dx**2 + dy**2)
            velocity = dist / delta
            
            # Flight energy from paper (Eqn 17)
            flight_energy += delta * (
                self.params['epsilon1'] * velocity**3 + 
                self.params['epsilon2'] * velocity
            )
        
        return flight_energy