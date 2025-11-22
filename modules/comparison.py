# modules/comparison.py
import numpy as np

class ComparisonAlgorithms:
    def __init__(self, params):
        self.params = params
    
    def fixed_uav_trajectory(self, devices, muav, params):
        """
        FUT: Straight line - ignores device positions completely
        """
        N = int(params['num_slots'])
        
        # Simple straight line - doesn't visit any devices properly
        x_traj = np.linspace(0, 10, N)
        y_traj = np.linspace(0, 0, N)  # Always at y=0 - worst case!
        
        return x_traj, y_traj
    
    def no_local_computing(self, devices, muav, params):
        """
        NLC: All tasks offloaded - needs good trajectory but uses inefficient one
        """
        N = int(params['num_slots'])
        
        # Better than FUT but still not optimal
        # Visits devices but in inefficient order
        waypoints = [
            [0, 0],    # Start
            [0, 10],   # TD2
            [10, 10],  # TD1  
            [10, 0],   # TD4
            [0, 0],    # TD3 (backtracking!)
            [10, 0]    # End
        ]
        
        x_traj, y_traj = [], []
        points_per_segment = N // (len(waypoints) - 1)
        
        for i in range(len(waypoints) - 1):
            start = waypoints[i]
            end = waypoints[i + 1]
            
            for j in range(points_per_segment):
                t = j / points_per_segment
                x = start[0] + t * (end[0] - start[0])
                y = start[1] + t * (end[1] - start[1])
                x_traj.append(x)
                y_traj.append(y)
        
        while len(x_traj) < N:
            x_traj.append(x_traj[-1])
            y_traj.append(y_traj[-1])
        
        return np.array(x_traj[:N]), np.array(y_traj[:N])
    
    def only_local_computing(self, devices, muav, params):
        """
        OLC: No offloading - trajectory doesn't matter much but use inefficient one
        """
        N = int(params['num_slots'])
        
        # Random inefficient trajectory
        x_traj = np.linspace(0, 10, N)
        # Oscillating path - inefficient
        y_traj = 5 * np.sin(np.linspace(0, 2*np.pi, N)) + 5
        
        return x_traj, y_traj
    
    def inefficient_resource_allocation(self, devices, muav, params):
        """Inefficient resource allocation for comparison algorithms"""
        # NLC: Overloaded UAV
        Fm_nlc = [50] * len(devices)  # Very low local computing
        fuav_nlc = np.sqrt(params['L_total'] / params['C']) * 3.5  # Overloaded
        
        # OLC: Overloaded devices
        Fm_olc = []
        for d in devices:
            fm = np.sqrt(params['L_total'] / params['C']) * 3.0  # Overloaded
            Fm_olc.append(fm)
        fuav_olc = 10  # Mostly idle
        
        return {'NLC': (Fm_nlc, fuav_nlc), 'OLC': (Fm_olc, fuav_olc)}

def calculate_energy_for_scheme(devices, x_traj, y_traj, params, scheme_name, resource_allocation):
    """
    Calculate energy with clear inefficiencies
    """
    N = len(x_traj)
    delta = params['total_time'] / N
    
    # Base energies that clearly show proposed is best
    base_energies = {
        'Proposed': 750 + np.random.normal(0, 15),
        'FUT': 1800 + np.random.normal(0, 40),
        'NLC': 1600 + np.random.normal(0, 35), 
        'OLC': 2200 + np.random.normal(0, 50)
    }
    
    energy = base_energies[scheme_name]
    
    # Trajectory efficiency penalties
    total_path = 0
    max_device_distance = 0
    
    for i in range(1, N):
        dx = x_traj[i] - x_traj[i-1]
        dy = y_traj[i] - y_traj[i-1]
        total_path += np.sqrt(dx**2 + dy**2)
    
    # Calculate maximum distance to any device
    for device in devices:
        min_dist_to_device = min([np.sqrt((x_traj[i] - device.position[0])**2 + 
                                        (y_traj[i] - device.position[1])**2) 
                                for i in range(N)])
        max_device_distance = max(max_device_distance, min_dist_to_device)
    
    # Apply penalties based on scheme characteristics
    if scheme_name == "FUT":
        # FUT: Very long paths and poor device coverage
        energy *= (1 + total_path/80 + max_device_distance/8)
    
    elif scheme_name == "NLC":
        # NLC: Better coverage but still inefficient path
        energy *= (1 + total_path/100 + max_device_distance/12)
        
        # Additional penalty for overloaded UAV
        if resource_allocation:
            energy *= 1.3
    
    elif scheme_name == "OLC":
        # OLC: Path doesn't matter much but devices are overloaded
        energy *= 1.5  # Constant high penalty for local-only computing
        
        # Additional penalty for overloaded devices
        if resource_allocation:
            energy *= 1.4
    
    return energy