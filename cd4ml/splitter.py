from cd4ml.utils.utils import hash_to_uniform_random
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def validate_splitting(ml_pipeline_params):
    """
    Validate the splitting data structure
    Ensures you are not validating data that you trained with.
    :param ml_pipeline_params: pipeline_params data structure
    :return: None
    """
    assert 'splitting' in ml_pipeline_params, "Missing 'splitting' configuration in ml_pipeline_params"
    splitting = ml_pipeline_params['splitting']

    # Check order
    assert splitting['training_random_start'] <= splitting['training_random_end'], \
        "Training range start must be <= training range end"
    assert splitting['validation_random_start'] <= splitting['validation_random_end'], \
        "Validation range start must be <= validation range end"

    # Check bounds
    assert 0 <= splitting['training_random_start'] <= 1, "Training range start must be within [0, 1]"
    assert 0 <= splitting['training_random_end'] <= 1, "Training range end must be within [0, 1]"
    assert 0 <= splitting['validation_random_start'] <= 1, "Validation range start must be within [0, 1]"
    assert 0 <= splitting['validation_random_end'] <= 1, "Validation range end must be within [0, 1]"

    # Check no overlap
    one = splitting['training_random_start'] >= splitting['validation_random_end']
    the_other = splitting['validation_random_start'] >= splitting['training_random_end']
    assert one or the_other, "Training and validation ranges must not overlap"

    logger.info(f"Splitting ranges validated successfully: {splitting}")


def splitter(ml_pipeline_params):
    """
    Splits data into training and validation sets based on hash value.
    :param ml_pipeline_params: dictionary containing splitting parameters
    :return: training_filter, validation_filter
    """
    identifier = ml_pipeline_params['identifier_field']
    splitting = ml_pipeline_params.get('splitting')

    if splitting is None:
        logger.warning("No splitting configuration found in ml_pipeline_params.")
        return None, None

    validate_splitting(ml_pipeline_params)

    seed = splitting['random_seed']
    train_start = splitting['training_random_start']
    train_end = splitting['training_random_end']
    validation_start = splitting['validation_random_start']
    validation_end = splitting['validation_random_end']

    def training_filter(row):
        try:
            hash_val = hash_to_uniform_random(row[identifier], seed)
            assert 0 <= hash_val < 1, f"Hash value out of bounds: {hash_val}"
            is_training = train_start <= hash_val < train_end
            logger.debug(f"Training filter applied: id={row[identifier]}, hash_val={hash_val}, is_training={is_training}")
            return is_training
        except KeyError:
            logger.error(f"Missing identifier '{identifier}' in row: {row}")
            raise
        except Exception as e:
            logger.error(f"Error applying training filter: {e}. Row: {row}")
            raise

    def validation_filter(row):
        try:
            hash_val = hash_to_uniform_random(row[identifier], seed)
            assert 0 <= hash_val < 1, f"Hash value out of bounds: {hash_val}"
            is_validation = validation_start <= hash_val < validation_end
            logger.debug(f"Validation filter applied: id={row[identifier]}, hash_val={hash_val}, is_validation={is_validation}")
            return is_validation
        except KeyError:
            logger.error(f"Missing identifier '{identifier}' in row: {row}")
            raise
        except Exception as e:
            logger.error(f"Error applying validation filter: {e}. Row: {row}")
            raise

    logger.info("Splitter filters created successfully.")
    logger.info(f"Training range: [{train_start}, {train_end}), Validation range: [{validation_start}, {validation_end})")

    return training_filter, validation_filter