from sklearn import metrics
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Funções de métrica

def r2_score(true_target, prediction):
    return metrics.r2_score(y_true=true_target, y_pred=prediction)

def rms_score(true_target, prediction):
    return np.sqrt(((np.array(prediction) - np.array(true_target))**2).mean())

def mad_score(true_target, prediction):
    return abs(np.array(prediction) - np.array(true_target)).mean()

def f1_score(true_target, prediction):
    return metrics.f1_score(true_target, prediction, average='macro')

def roc_auc(true_target, prediction_prob, target_levels):
    return metrics.roc_auc_score(true_target, prediction_prob,
                                 multi_class='ovo', labels=target_levels)

def get_num_validated(true_target, _):
    return len(true_target)

# Mapeamento de funções de métrica
metric_funcs = {
    'roc_auc': {'function': roc_auc, 'runs_on': 'prob'},
    'r2_score': {'function': r2_score, 'runs_on': 'pred'},
    'rms_score': {'function': rms_score, 'runs_on': 'pred'},
    'mad_score': {'function': mad_score, 'runs_on': 'pred'},
    'f1_score': {'function': f1_score, 'runs_on': 'pred'},
    'num_validated': {'function': get_num_validated, 'runs_on': 'pred'}
}

# Funções auxiliares

def get_metric(metric_name, true_target, prediction, pred_prob, target_levels):
    func = metric_funcs[metric_name]['function']
    runs_on = metric_funcs[metric_name]['runs_on']

    if runs_on == 'prob':
        metric = func(true_target, pred_prob, target_levels)
    elif runs_on == 'pred':
        metric = func(true_target, prediction)
    else:
        raise ValueError(f"Unknown runs_on value: {runs_on}")

    logger.info(f'{metric_name}: {metric}')
    return metric

def get_validation_metrics(metric_names, true_target, prediction, pred_prob, target_levels):
    # Verificar se o conjunto de validação está vazio
    if not true_target or len(true_target) == 0:
        logger.error("O conjunto de validação está vazio. Verifique os dados de entrada.")
        raise ValueError("O conjunto de validação está vazio. Não é possível calcular métricas de validação.")

    n_validated = len(true_target)
    logger.info(f'Número de validações: {n_validated}')

    # Calcular métricas de validação
    validation_metrics = {
        metric_name: get_metric(metric_name, true_target, prediction, pred_prob, target_levels)
        for metric_name in metric_names
    }

    logger.info('Métricas de validação concluídas')
    return validation_metrics