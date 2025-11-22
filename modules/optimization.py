import numpy as np
import cvxpy as cp

# ----------------------------
# Resource Allocation Function
# ----------------------------
def optimize_resource_allocation(devices, muav, params):
    """
    Simplified function to assign computation frequencies
    for each terminal device and the MUAV.
    """
    Fm = []
    for d in devices:
        # Simple deterministic allocation
        fm = np.sqrt(params['L_total'] / params['C'])
        Fm.append(fm)
        d.compute_local_energy(fm)

    fuav = np.mean(Fm) * 1.2
    return Fm, fuav


# ----------------------------
# Trajectory Optimization Function
# ----------------------------
def optimize_trajectory(muav, devices, params):
    """
    Convex trajectory optimization (simplified DCP-compliant).
    """
    N = int(params['num_slots'])
    Vmax = float(params['Vmax'])
    delta = float(params['total_time']) / N

    # Decision variables for UAV path
    x = cp.Variable(N)
    y = cp.Variable(N)

    # Boundary constraints
    constraints = [
        x[0] == 0, y[0] == 0,
        x[-1] == 10, y[-1] == 0
    ]

    # Velocity constraints using DQCP
    for i in range(1, N):
        v_sq = ((x[i] - x[i-1])**2 + (y[i] - y[i-1])**2) / (delta**2)
        # Use cp.norm for DQCP compliance
        v = cp.norm(cp.vstack([(x[i] - x[i-1])/delta, (y[i] - y[i-1])/delta]))
        constraints += [v <= Vmax]

    # Objective: minimize total squared distance to devices + some regularization
    objective = 0
    for i in range(N):
        for d in devices:
            dist_sq = (x[i] - d.position[0])**2 + (y[i] - d.position[1])**2
            objective += dist_sq
    
    # Add small regularization for smoothness
    for i in range(1, N):
        objective += 0.01 * ((x[i] - x[i-1])**2 + (y[i] - y[i-1])**2)

    # Solve as QCP problem
    prob = cp.Problem(cp.Minimize(objective), constraints)
    prob.solve(solver=cp.SCS, verbose=True, qcp=True, max_iters=2000)

    if prob.status not in ["optimal", "optimal_inaccurate"]:
        print(f"Warning: Solution status: {prob.status}")
        # Return a straight line trajectory as fallback
        x_fallback = np.linspace(0, 10, N)
        y_fallback = np.linspace(0, 0, N)
        return x_fallback, y_fallback

    return x.value, y.value
