from backend.calculators.project_estimator import estimate_cost

def project_tool(area_sqft, cost_per_sqft):
    return estimate_cost(area_sqft, cost_per_sqft)