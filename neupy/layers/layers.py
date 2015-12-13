import theano
import theano.tensor as T

from neupy.utils import asfloat
from neupy.core.properties import (TypedListProperty, ArrayProperty,
                                   ChoiceProperty)
from neupy.layers.base import BaseLayer
from neupy.layers.utils import GAUSSIAN, VALID_INIT_METHODS, generate_weight


__all__ = ('Layer', 'Linear', 'Sigmoid', 'Step', 'Tanh', 'Relu', 'Softplus',
           'Softmax')


theano_shared_class = T.sharedvar.TensorSharedVariable


class SharedArrayProperty(ArrayProperty):
    """ In addition to Numpy arrays and matrix property support also
    Theano shared variables.

    Parameters
    ----------
    {BaseProperty.default}
    {BaseProperty.required}
    """
    expected_type = (ArrayProperty.expected_type, theano_shared_class)


class Layer(BaseLayer):
    """ Base class for input and hidden layers.
    Parameters
    ----------
    {BaseLayer.input_size}
    weight : 2D array-like or None
        Define your layer weights. ``None`` means that your weights will be
        generate randomly dependence on property ``init_method``.
        ``None`` by default.
    bias : 1D array-like or None
        Define your layer bias. ``None`` means that your weights will be
        generate randomly dependence on property ``init_method``.
    init_method : {{'gauss', 'bounded', 'ortho'}}
        Weight initialization method.
        ``gauss`` will generate random weights from Standard Normal
        Distribution.
        ``bounded`` generate random weights from Uniform distribution.
        ``ortho`` generate random orthogonal matrix.
        Defaults to ``gauss``.
    bounds : tuple of two float
        Available only for ``init_method`` eqaul to ``bounded``.  Value
        identify minimum and maximum possible value in random weights.
        Defaults to ``(0, 1)``.
    """
    weight = SharedArrayProperty(default=None)
    bias = SharedArrayProperty(default=None)
    bounds = TypedListProperty(default=(0, 1), element_type=(int, float))
    init_method = ChoiceProperty(default=GAUSSIAN, choices=VALID_INIT_METHODS)

    def initialize(self):
        output_size = self.relate_to_layer.input_size
        weight = self.weight
        bias = self.bias
        self.step = None

        if self.relate_from_layer is not None:
            self.layer_id = self.relate_from_layer.layer_id + 1

        self.weight_shape = (self.input_size, output_size)
        self.bias_shape = (output_size,)

        # TODO: This part looks ugly, should find a different way.
        if not isinstance(weight, theano_shared_class):
            if weight is None:
                weight = generate_weight(self.weight_shape, self.bounds,
                                         self.init_method)

            self.weight = theano.shared(value=asfloat(weight),
                                        name='weight_{}'.format(self.layer_id),
                                        borrow=True)

        if not isinstance(bias, theano_shared_class):
            if bias is None:
                bias = generate_weight(self.bias_shape, self.bounds,
                                       self.init_method)

            self.bias = theano.shared(value=asfloat(bias),
                                      name='bias_{}'.format(self.layer_id),
                                      borrow=True)

        self.parameters = [self.weight, self.bias]

    def output(self, input_value):
        summated = T.dot(input_value, self.weight) + self.bias
        return self.activation_function(summated)


class Linear(Layer):
    """ The layer with the linear activation function.

    Parameters
    ----------
    {BaseLayer.input_size}
    {Layer.weight}
    {Layer.bias}
    {Layer.init_method}
    {Layer.bounds}
    """
    activation_function = (lambda x: x)


class Sigmoid(Layer):
    """ The layer with the sigmoid activation function.

    Parameters
    ----------
    {BaseLayer.input_size}
    {Layer.weight}
    {Layer.bias}
    {Layer.init_method}
    {Layer.bounds}
    """
    activation_function = T.nnet.sigmoid


def step_function(value):
    """ Step activation function.
    """
    return T.gt(value, 0)


class Step(Layer):
    """ The layer with the the step activation function.

    Parameters
    ----------
    {BaseLayer.input_size}
    {Layer.weight}
    {Layer.bias}
    {Layer.init_method}
    {Layer.bounds}
    """
    activation_function = step_function


class Tanh(Layer):
    """ The layer with the `tanh` activation function.

    Parameters
    ----------
    {BaseLayer.input_size}
    {Layer.weight}
    {Layer.bias}
    {Layer.init_method}
    {Layer.bounds}
    """
    activation_function = T.tanh


class Relu(Layer):
    """ The layer with the rectifier activation function.

    Parameters
    ----------
    {BaseLayer.input_size}
    {Layer.weight}
    {Layer.bias}
    {Layer.init_method}
    {Layer.bounds}
    """
    activation_function = T.nnet.relu


class Softplus(Layer):
    """ The layer with the softplus activation function.

    Parameters
    ----------
    {BaseLayer.input_size}
    {Layer.weight}
    {Layer.bias}
    {Layer.init_method}
    {Layer.bounds}
    """
    activation_function = T.nnet.softplus


class Softmax(Layer):
    """ The layer with the softmax activation function.

    Parameters
    ----------
    {BaseLayer.input_size}
    {Layer.weight}
    {Layer.bias}
    {Layer.init_method}
    {Layer.bounds}
    """
    activation_function = T.nnet.softmax
