import yaml
import matplotlib.pyplot as plt
import numpy as np


def load_config(path='config.yaml'):
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    params = data['simulation']

    # Convert numeric strings like '30e6' into float
    for k, v in params.items():
        try:
            params[k] = float(v)
        except (ValueError, TypeError):
            pass
    return params


def plot_trajectory(x, y, devices, save_path='results/trajectory.png'):
    plt.figure(figsize=(12, 5))
    
    # Plot 1: Trajectory
    plt.subplot(1, 2, 1)
    plt.plot(x, y, '-o', markersize=3, label='MUAV Trajectory')
    for d in devices:
        plt.scatter(d.position[0], d.position[1], label=f'TD{d.id}', s=100)
    plt.xlabel('x (m)')
    plt.ylabel('y (m)')
    plt.title('Optimized MUAV Trajectory')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    
    # Plot 2: Velocity profile
    plt.subplot(1, 2, 2)
    velocities = []
    for i in range(1, len(x)):
        dx = x[i] - x[i-1]
        dy = y[i] - y[i-1]
        v = np.sqrt(dx**2 + dy**2) / 0.04  # assuming delta=0.04 from your output
        velocities.append(v)
    
    plt.plot(range(len(velocities)), velocities, 'r-')
    plt.axhline(y=10, color='g', linestyle='--', label='Vmax constraint')
    plt.xlabel('Time step')
    plt.ylabel('Velocity (m/s)')
    plt.title('Velocity Profile')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


# modules/utils.py (add this function)


def plot_comparison(proposed_trajectory, comparison_trajectories, devices, energy_results, save_path='results/comparison.png'):
    """
    Plot comparison between proposed algorithm and other schemes
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Trajectories comparison
    x_proposed, y_proposed = proposed_trajectory
    ax1.plot(x_proposed, y_proposed, '-o', markersize=3, linewidth=2, label='Proposed', color='red')
    
    colors = ['blue', 'green', 'orange', 'purple', 'brown']
    for i, (algo, trajectory) in enumerate(comparison_trajectories.items()):
        x, y = trajectory
        ax1.plot(x, y, '--', markersize=2, linewidth=1.5, label=algo, color=colors[i % len(colors)])
    
    # Plot devices
    for d in devices:
        ax1.scatter(d.position[0], d.position[1], s=100, label=f'TD{d.id}', alpha=0.7)
    
    ax1.set_xlabel('x (m)')
    ax1.set_ylabel('y (m)')
    ax1.set_title('Trajectory Comparison')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.axis('equal')
    
    # Plot 2: Energy consumption comparison
    algorithms = list(energy_results.keys())
    energies = list(energy_results.values())
    
    bars = ax2.bar(algorithms, energies, color=['red', 'blue', 'green', 'orange', 'purple'][:len(algorithms)])
    ax2.set_xlabel('Algorithms')
    ax2.set_ylabel('Energy Consumption (J)')
    ax2.set_title('Energy Consumption Comparison')
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, energy in zip(bars, energies):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{energy:.1f} J', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Also create a separate energy comparison plot
    plt.figure(figsize=(10, 6))
    bars = plt.bar(algorithms, energies, color=['red', 'blue', 'green', 'orange', 'purple'][:len(algorithms)])
    plt.xlabel('Algorithms')
    plt.ylabel('Energy Consumption (J)')
    plt.title('Energy Consumption Comparison of Different Algorithms')
    plt.grid(True, alpha=0.3)
    
    for bar, energy in zip(bars, energies):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{energy:.1f} J', ha='center', va='bottom')
    
    plt.savefig('results/energy_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    
# # Add this to modules/utils.py
# def plot_trajectory_comparison(proposed_trajectory, comparison_trajectories, devices, save_path='results/trajectory_comparison.png'):
#     """Enhanced trajectory comparison plot"""
#     fig, axes = plt.subplots(2, 2, figsize=(15, 12))
#     axes = axes.flatten()
    
#     trajectories = [('Proposed', proposed_trajectory)] + list(comparison_trajectories.items())
    
#     for idx, (algo, trajectory) in enumerate(trajectories):
#         if idx >= 4:
#             break
            
#         x, y = trajectory
#         ax = axes[idx]
        
#         # Plot trajectory
#         ax.plot(x, y, 'o-', markersize=3, linewidth=2, label=f'{algo} Trajectory')
        
#         # Plot devices
#         for d in devices:
#             ax.scatter(d.position[0], d.position[1], s=150, label=f'TD{d.id}', alpha=0.8)
        
#         # Add start and end markers
#         ax.scatter(x[0], y[0], s=200, marker='^', color='green', label='Start')
#         ax.scatter(x[-1], y[-1], s=200, marker='v', color='red', label='End')
        
#         ax.set_xlabel('x (m)')
#         ax.set_ylabel('y (m)')
#         ax.set_title(f'{algo} Algorithm\nTrajectory', fontsize=12, fontweight='bold')
#         ax.legend()
#         ax.grid(True, alpha=0.3)
#         ax.axis('equal')
#         ax.set_xlim(-2, 12)
#         ax.set_ylim(-2, 12)
    
#     plt.tight_layout()
#     plt.savefig(save_path, dpi=300, bbox_inches='tight')
#     plt.close()
    
    

# # Add to modules/utils.py
# def plot_enhanced_comparison(proposed_trajectory, comparison_trajectories, devices, energy_results, save_path='results/enhanced_comparison.png'):
#     """
#     Enhanced comparison plot showing clear trajectory differences
#     """
#     fig = plt.figure(figsize=(16, 12))
    
#     # Create subplot grid
#     gs = plt.GridSpec(3, 2, figure=fig)
    
#     # Plot 1: All trajectories together
#     ax1 = fig.add_subplot(gs[0, :])
#     x_proposed, y_proposed = proposed_trajectory
    
#     # Plot proposed trajectory
#     ax1.plot(x_proposed, y_proposed, 'r-', linewidth=3, marker='o', markersize=4, label='Proposed (Triangular)', alpha=0.8)
    
#     # Plot comparison trajectories
#     colors = ['blue', 'green', 'orange']
#     linestyles = ['--', '-.', ':']
#     for i, (algo, trajectory) in enumerate(comparison_trajectories.items()):
#         x, y = trajectory
#         ax1.plot(x, y, linestyles[i], color=colors[i], linewidth=2, label=f'{algo}', alpha=0.7)
    
#     # Plot devices
#     for d in devices:
#         ax1.scatter(d.position[0], d.position[1], s=200, label=f'TD{d.id}', alpha=0.8, edgecolors='black')
    
#     ax1.set_xlabel('x (m)')
#     ax1.set_ylabel('y (m)')
#     ax1.set_title('Trajectory Comparison: Proposed vs Benchmark Algorithms', fontsize=14, fontweight='bold')
#     ax1.legend()
#     ax1.grid(True, alpha=0.3)
#     ax1.axis('equal')
#     ax1.set_xlim(-2, 12)
#     ax1.set_ylim(-2, 14)
    
#     # Plot 2: Energy comparison
#     ax2 = fig.add_subplot(gs[1, 0])
#     algorithms = list(energy_results.keys())
#     energies = list(energy_results.values())
    
#     colors = ['green', 'red', 'orange', 'purple']
#     bars = ax2.bar(algorithms, energies, color=colors[:len(algorithms)], alpha=0.7)
#     ax2.set_xlabel('Algorithms')
#     ax2.set_ylabel('Energy Consumption (J)')
#     ax2.set_title('Energy Consumption Comparison', fontweight='bold')
#     ax2.grid(True, alpha=0.3)
    
#     # Add value labels
#     for bar, energy in zip(bars, energies):
#         height = bar.get_height()
#         ax2.text(bar.get_x() + bar.get_width()/2., height + 50,
#                 f'{energy:.0f} J', ha='center', va='bottom', fontweight='bold')
    
#     # Plot 3: Energy savings
#     ax3 = fig.add_subplot(gs[1, 1])
#     proposed_energy = energy_results['Proposed']
#     savings = []
#     labels = []
    
#     for algo, energy in energy_results.items():
#         if algo != 'Proposed':
#             saving = ((energy - proposed_energy) / energy) * 100
#             savings.append(saving)
#             labels.append(algo)
    
#     colors = ['red', 'orange', 'purple']
#     bars = ax3.bar(labels, savings, color=colors, alpha=0.7)
#     ax3.set_xlabel('Algorithms')
#     ax3.set_ylabel('Energy Saving (%)')
#     ax3.set_title('Energy Savings vs Proposed Algorithm', fontweight='bold')
#     ax3.grid(True, alpha=0.3)
    
#     for bar, saving in zip(bars, savings):
#         height = bar.get_height()
#         ax3.text(bar.get_x() + bar.get_width()/2., height + 2,
#                 f'{saving:.1f}%', ha='center', va='bottom', fontweight='bold')
    
#     # Plot 4: Trajectory efficiency metrics
#     ax4 = fig.add_subplot(gs[2, :])
    
#     # Calculate efficiency metrics
#     algorithms = ['Proposed'] + list(comparison_trajectories.keys())
#     trajectories = [proposed_trajectory] + [traj for traj in comparison_trajectories.values()]
    
#     path_lengths = []
#     avg_distances = []
    
#     for (algo, (x, y)) in zip(algorithms, trajectories):
#         # Calculate total path length
#         total_path = 0
#         for i in range(1, len(x)):
#             dx = x[i] - x[i-1]
#             dy = y[i] - y[i-1]
#             total_path += np.sqrt(dx**2 + dy**2)
#         path_lengths.append(total_path)
        
#         # Calculate average distance to devices
#         total_avg_dist = 0
#         for device in devices:
#             min_dists = [np.sqrt((x[i] - device.position[0])**2 + (y[i] - device.position[1])**2) 
#                         for i in range(len(x))]
#             total_avg_dist += np.mean(min_dists)
#         avg_distances.append(total_avg_dist / len(devices))
    
#     # Plot metrics
#     x_pos = np.arange(len(algorithms))
#     width = 0.35
    
#     ax4.bar(x_pos - width/2, path_lengths, width, label='Total Path Length (m)', alpha=0.7)
#     ax4.bar(x_pos + width/2, avg_distances, width, label='Avg Device Distance (m)', alpha=0.7)
    
#     ax4.set_xlabel('Algorithms')
#     ax4.set_ylabel('Metrics (m)')
#     ax4.set_title('Trajectory Efficiency Metrics', fontweight='bold')
#     ax4.set_xticks(x_pos)
#     ax4.set_xticklabels(algorithms)
#     ax4.legend()
#     ax4.grid(True, alpha=0.3)
    
#     plt.tight_layout()
#     plt.savefig(save_path, dpi=300, bbox_inches='tight')
#     plt.close()