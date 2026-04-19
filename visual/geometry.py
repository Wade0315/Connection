import numpy as np
def get_arc_midpoint(p1, p2, rad):
    p1, p2 = np.array(p1), np.array(p2)
    mid = (p1 + p2) / 2.0
    diff = p2 - p1
    perp = np.array([-diff[1], diff[0]])
    # 這是弧線最彎的地方（t=0.5 處的座標）
    # 公式簡化後：中點 + 0.5 * rad * perp
    control_p = mid + rad * perp
    # 二次貝茲曲線在 t=0.5 時的公式為: 0.25*p1 + 0.5*control + 0.25*p2
    arc_mid = 0.25*p1 + 0.5*control_p + 0.25*p2
    return arc_mid


def get_arc_path(p0, p2, rad, num_points=20):
    p0, p2 = np.array(p0), np.array(p2)
    if rad == 0: 
        return np.linspace(p0, p2, num_points)
    mid = (p0 + p2) / 2.0
    diff = p2 - p0
    perp = np.array([-diff[1], diff[0]])
    control_p = mid + rad * perp
    
    t = np.linspace(0, 1, num_points)
    # 二次貝茲公式
    return (1-t)[:, None]**2 * p0 + 2*(1-t)[:, None]*t[:, None]*control_p + t[:, None]**2 * p2