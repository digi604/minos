'''
Created on Feb 18, 2017

@author: julien
'''
import tempfile
import unittest

from minos.experiment.experiment import ExperimentParameters, Experiment
from minos.experiment.training import Training, EpochStoppingCondition,\
    AccuracyDecreaseStoppingCondition
from minos.model.build import ModelBuilder
from minos.model.design import create_random_blueprint
from minos.model.model import Layout, Objective, Optimizer, Metric
from minos.train.utils import default_device, CpuEnvironment
from minos.utils import disable_sysout
from tests.fixtures import get_reuters_dataset


class TrainTest(unittest.TestCase):

    def test_train(self):
        disable_sysout()
        with tempfile.TemporaryDirectory() as tmp_dir:
            batch_size = 50
            batch_iterator, test_batch_iterator, nb_classes = get_reuters_dataset(batch_size, 1000)
            layout = Layout(
                input_size=1000,
                output_size=nb_classes,
                output_activation='softmax')
            training = Training(
                objective=Objective('categorical_crossentropy'),
                optimizer=Optimizer(optimizer='Adam'),
                metric=Metric('categorical_accuracy'),
                stopping=EpochStoppingCondition(10),
                batch_size=batch_size)
            experiment_parameters = ExperimentParameters(use_default_values=True)
            experiment_parameters.layout_parameter('rows', 1)
            experiment_parameters.layout_parameter('blocks', 1)
            experiment_parameters.layout_parameter('layers', 1)
            experiment = Experiment(
                'test__reuters_experiment',
                layout,
                training,
                batch_iterator,
                test_batch_iterator,
                CpuEnvironment(n_jobs=1, data_dir=tmp_dir),
                parameters=experiment_parameters)

            blueprint = create_random_blueprint(experiment)
            model = ModelBuilder().build(blueprint, default_device())
            result = model.fit_generator(
                generator=batch_iterator,
                samples_per_epoch=batch_iterator.samples_per_epoch,
                nb_epoch=10,
                validation_data=test_batch_iterator,
                nb_val_samples=test_batch_iterator.sample_count)
            self.assertIsNotNone(
                result,
                'should have fit the model')
            score = model.evaluate_generator(
                test_batch_iterator,
                val_samples=test_batch_iterator.sample_count)
            self.assertIsNotNone(
                score,
                'should have evaluated the model')

    def test_early_stopping_condition_test(self):
        disable_sysout()
        with tempfile.TemporaryDirectory() as tmp_dir:
            batch_size = 50
            batch_iterator, test_batch_iterator, nb_classes = get_reuters_dataset(batch_size, 1000)
            layout = Layout(
                input_size=1000,
                output_size=nb_classes,
                output_activation='softmax')
            training = Training(
                objective=Objective('categorical_crossentropy'),
                optimizer=Optimizer(optimizer='Adam'),
                metric=Metric('categorical_accuracy'),
                stopping=AccuracyDecreaseStoppingCondition(
                    noprogress_count=2,
                    min_epoch=1,
                    max_epoch=5),
                batch_size=batch_size)
            experiment_parameters = ExperimentParameters(use_default_values=True)
            experiment_parameters.layout_parameter('rows', 1)
            experiment_parameters.layout_parameter('blocks', 1)
            experiment_parameters.layout_parameter('layers', 1)
            experiment = Experiment(
                'test__reuters_experiment',
                layout,
                training,
                batch_iterator,
                test_batch_iterator,
                CpuEnvironment(n_jobs=1, data_dir=tmp_dir),
                parameters=experiment_parameters)

            blueprint = create_random_blueprint(experiment)
            model = ModelBuilder().build(blueprint, default_device())
            result = model.fit_generator(
                generator=batch_iterator,
                samples_per_epoch=batch_iterator.samples_per_epoch,
                nb_epoch=10,
                validation_data=test_batch_iterator,
                nb_val_samples=test_batch_iterator.sample_count)
            self.assertIsNotNone(
                result,
                'should have fit the model')
            score = model.evaluate_generator(
                test_batch_iterator,
                val_samples=test_batch_iterator.sample_count)
            self.assertIsNotNone(
                score,
                'should have evaluated the model')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
