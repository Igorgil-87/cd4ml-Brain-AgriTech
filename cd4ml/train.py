import logging
from cd4ml.available_models import get_algorithm_class

logger = logging.getLogger(__name__)

def train_model(encoded_train_data, target, model_name, params, seed=None):
    """
    Treina o modelo com os dados codificados e o alvo.
    """
    model_class = get_algorithm_class(model_name)

    logger.info("Training {} model".format(model_name))

    # Remove 'random_state' de params se já existir
    params = params.copy()  # Evitar modificar o dicionário original
    if 'random_state' in params:
        logger.warning("Removendo 'random_state' de params para evitar conflito.")
        del params['random_state']

    # Passa o argumento random_state separadamente
    clf = model_class(random_state=seed, **params)

    # Treina o modelo
    trained_model = clf.fit(encoded_train_data, target)
    return trained_model


def get_trained_model(algorithm_name,
                      algorithm_params,
                      encoded_train_data,
                      target_data,
                      seed):
    """
    Obtém o modelo treinado usando os dados fornecidos.
    """
    n_rows = len(encoded_train_data)
    n_cols = len(encoded_train_data[0])
    logger.info('n_rows: %s, n_cols: %s' % (n_rows, n_cols))

    trained_model = train_model(encoded_train_data, target_data, algorithm_name,
                                algorithm_params, seed=seed)

    return trained_model