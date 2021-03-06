from FIAT.reference_element import UFCQuadrilateral

from gem.utils import cached_property

from finat.finiteelementbase import FiniteElementBase


class QuadrilateralElement(FiniteElementBase):
    """Class for elements on quadrilaterals.  Wraps a tensor product
    element on an interval x interval cell, but appears on a
    quadrilateral cell to the outside world."""

    def __init__(self, element):
        super(QuadrilateralElement, self).__init__()
        self.product = element

    @cached_property
    def cell(self):
        return UFCQuadrilateral()

    @property
    def degree(self):
        unique_degree, = set(self.product.degree)
        return unique_degree

    @property
    def formdegree(self):
        return self.product.formdegree

    @cached_property
    def _entity_dofs(self):
        return flatten(self.product.entity_dofs())

    @cached_property
    def _entity_support_dofs(self):
        return flatten(self.product.entity_support_dofs())

    def entity_dofs(self):
        return self._entity_dofs

    def space_dimension(self):
        return self.product.space_dimension()

    def basis_evaluation(self, order, ps, entity=None):
        """Return code for evaluating the element at known points on the
        reference element.

        :param order: return derivatives up to this order.
        :param ps: the point set object.
        :param entity: the cell entity on which to tabulate.
        """
        return self.product.basis_evaluation(order, ps, productise(entity))

    def point_evaluation(self, order, point, entity=None):
        return self.product.point_evaluation(order, point, productise(entity))

    @property
    def index_shape(self):
        return self.product.index_shape

    @property
    def value_shape(self):
        return self.product.value_shape

    @property
    def mapping(self):
        return self.product.mapping


def flatten(dofs):
    flat_dofs = {}
    flat_dofs[0] = dofs[(0, 0)]
    flat_dofs[1] = dict(enumerate(
        [v for k, v in sorted(dofs[(0, 1)].items())] +
        [v for k, v in sorted(dofs[(1, 0)].items())]
    ))
    flat_dofs[2] = dofs[(1, 1)]
    return flat_dofs


def productise(entity):
    if entity is None:
        entity = (2, 0)

    # Entity is provided in flattened form (d, i)
    # We factor the entity and construct an appropriate
    # entity id for a TensorProductCell: ((d1, d2), i)
    entity_dim, entity_id = entity
    if entity_dim == 2:
        assert entity_id == 0
        return ((1, 1), 0)
    elif entity_dim == 1:
        facets = [((0, 1), 0),
                  ((0, 1), 1),
                  ((1, 0), 0),
                  ((1, 0), 1)]
        return facets[entity_id]
    elif entity_dim == 0:
        return ((0, 0), entity_id)
    else:
        raise ValueError("Illegal entity dimension %s" % entity_dim)
