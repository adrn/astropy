# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import (absolute_import, unicode_literals, division,
                        print_function)

import numpy as np

from ... import units as u
from ...time import Time
from ..representation import (CartesianRepresentation,
                              SphericalRepresentation,
                              UnitSphericalRepresentation,
                              SphericalCosLatDifferential,
                              UnitSphericalCosLatDifferential)
from ..baseframe import (BaseCoordinateFrame, RepresentationMapping,
                         frame_transform_graph)
from ..transformations import AffineTransform
from ..frame_attributes import VelocityAttribute

from .icrs import ICRS
from .galactic import Galactic

# For speed
J2000 = Time('J2000')

v_bary_Schoenrich2010 = CartesianRepresentation([-11.1, 12.24, 7.25]*u.km/u.s)

__all__ = ['LSR']

class LSR(BaseCoordinateFrame):
    """
    A coordinate or frame in the Local Standard of Rest (LSR).

    TODO: more words
    - axis-aligned with ICRS
    - co-spatial (SS barycenter)

    Parameters
    ----------
    representation : `BaseRepresentation` or None
        A representation object or None to have no data (or use the other keywords)
    ra : `Angle`, optional, must be keyword
        The RA for this object (``dec`` must also be given and ``representation``
        must be None).
    dec : `Angle`, optional, must be keyword
        The Declination for this object (``ra`` must also be given and
        ``representation`` must be None).
    distance : `~astropy.units.Quantity`, optional, must be keyword
        The Distance for this object along the line-of-sight.
        (``representation`` must be None).
    copy : bool, optional
        If `True` (default), make copies of the input coordinate arrays.
        Can only be passed in as a keyword argument.
    """

    frame_specific_representation_info = {
        SphericalRepresentation: [
            RepresentationMapping('lon', 'ra'),
            RepresentationMapping('lat', 'dec')
        ],
        SphericalCosLatDifferential: [
            RepresentationMapping('d_lon_coslat', 'pm_ra'), # TODO: change names because LSR?
            RepresentationMapping('d_lat', 'pm_dec'),
            RepresentationMapping('d_distance', 'radial_velocity'),
        ],

    }
    frame_specific_representation_info[UnitSphericalRepresentation] = \
        frame_specific_representation_info[SphericalRepresentation]
    frame_specific_representation_info[UnitSphericalCosLatDifferential] = \
        frame_specific_representation_info[SphericalCosLatDifferential]

    default_representation = SphericalRepresentation
    default_differential = SphericalCosLatDifferential

    # frame attributes:
    v_bary = VelocityAttribute(Galactic,
                               default=Galactic(v_bary_Schoenrich2010))


@frame_transform_graph.transform(AffineTransform, ICRS, LSR)
def icrs_to_lsr(icrs_coord, lsr_frame):
    voffset = lsr_frame.v_bary.transform_to(icrs_coord)
    return None, (None, voffset.cartesian.get_xyz())

@frame_transform_graph.transform(AffineTransform, LSR, ICRS)
def lsr_to_icrs(lsr_coord, icrs_frame):
    voffset = lsr_coord.v_bary.transform_to(icrs_frame)
    return None, (None, -voffset.cartesian.get_xyz())