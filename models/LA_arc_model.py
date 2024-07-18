from models.customer_model import Customer


class LA_arc:
    def __init__(self, u: Customer, N_p: set, v: Customer):
        self.u = u
        self.N_p = N_p
        self.v = v

    def __repr__(self):
        return f"LA_arc(u={self.u}, N_p={self.N_p}, v={self.v})"

    def __eq__(self, other):
        if isinstance(other, LA_arc):
            return ((self.u == other.u) and (self.v == other.v) and (set(self.N_p).issubset(set(other.N_p))) and (set(other.N_p).issubset(set(self.N_p))))
        else:
            return False

    def __hash__(self):
        return hash((self.u, frozenset(self.N_p), self.v))
