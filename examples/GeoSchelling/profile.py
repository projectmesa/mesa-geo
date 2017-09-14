from model import SchellingModel


def run():
    model_params = {
            "density": 0.8,
            "minority_pc": 0.2
        }

    M = SchellingModel(**model_params)

    for i in range(2):
        M.step()

    return M
