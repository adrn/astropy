# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

# TEST_UNICODE_LITERALS

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

"""Test initalization and other aspects of Angle and subclasses"""

import numpy as np
from numpy.testing.utils import assert_allclose

from ..angles import Longitude, Latitude, Angle
from ...tests.helper import pytest
from ... import units as u
from ..errors import IllegalSecondError, IllegalMinuteError, IllegalHourError


def test_create_angles():
    """
    Tests creating and accessing Angle objects
    """

    ''' The "angle" is a fundamental object. The internal
    representation is stored in radians, but this is transparent to the user.
    Units *must* be specified rather than a default value be assumed. This is
    as much for self-documenting code as anything else.

    Angle objects simply represent a single angular coordinate. More specific
    angular coordinates (e.g. Longitude, Latitude) are subclasses of Angle.'''

    a1 = Angle(54.12412, unit=u.degree)
    a2 = Angle("54.12412", unit=u.degree)
    a3 = Angle("54:07:26.832", unit=u.degree)
    a4 = Angle("54.12412 deg")
    a5 = Angle("54.12412 degrees")
    a6 = Angle("54.12412°") # because we like Unicode
    a7 = Angle((54, 7, 26.832), unit=u.degree)
    a8 = Angle("54°07'26.832\"")
    # (deg,min,sec) *tuples* are acceptable, but lists/arrays are *not*
    # because of the need to eventually support arrays of coordinates
    a9 = Angle([54, 7, 26.832], unit=u.degree)
    assert_allclose(a9.value, [54, 7, 26.832])
    assert a9.unit is u.degree

    a10 = Angle(3.60827466667, unit=u.hour)
    a11 = Angle("3:36:29.7888000120", unit=u.hour)
    a12 = Angle((3, 36, 29.7888000120), unit=u.hour)  # *must* be a tuple

    Angle(0.944644098745, unit=u.radian)

    with pytest.raises(u.UnitsError):
        Angle(54.12412)
        #raises an exception because this is ambiguous

    with pytest.raises(ValueError):
        a13 = Angle(12.34, unit="not a unit")

    a14 = Angle("12h43m32") # no trailing 's', but unambiguous

    a15 = Angle("5h4m3s") # single digits, no decimal

    a16 = Angle("1 d")
    a17 = Angle("1 degree")
    assert a16.degree == 1
    assert a17.degree == 1

    #ensure the above angles that should match do
    assert a1 == a2 == a3 == a4 == a5 == a6 == a7
    assert_allclose(a1.radian, a2.radian)
    assert_allclose(a2.degree, a3.degree)
    assert_allclose(a3.radian, a4.radian)
    assert_allclose(a4.radian, a5.radian)
    assert_allclose(a5.radian, a6.radian)
    assert_allclose(a6.radian, a7.radian)
    #assert a10 == a11 == a12

    # check for illegal ranges / values
    with pytest.raises(IllegalSecondError):
        a = Angle("12 32 99", unit=u.degree)

    with pytest.raises(IllegalMinuteError):
        a = Angle("12 99 23", unit=u.degree)

    with pytest.raises(IllegalSecondError):
        a = Angle("12 32 99", unit=u.hour)

    with pytest.raises(IllegalMinuteError):
        a = Angle("12 99 23", unit=u.hour)

    with pytest.raises(IllegalHourError):
        a = Angle("99 25 51.0", unit=u.hour)

    with pytest.raises(ValueError):
        a = Angle("12 25 51.0xxx", unit=u.hour)

    with pytest.raises(ValueError):
        a = Angle("12h34321m32.2s")

    assert a1 is not None

def test_angle_ops():
    """
    Tests operations on Angle objects
    """

    # Angles can be added and subtracted. Multiplication and division by a
    # scalar is also permitted. A negative operator is also valid.  All of
    # these operate in a single dimension. Attempting to multiply or divide two
    # Angle objects will raise an exception.

    a1 = Angle(3.60827466667, unit=u.hour)
    a2 = Angle("54:07:26.832", unit=u.degree)
    a1 + a2  # creates new Angle object
    a1 - a2
    -a1

    # division and multiplication have no unambiguous meaning here
    with pytest.raises(TypeError):
        a1 / a2

    with pytest.raises(TypeError):
        a1 * a2

    assert_allclose((a1 * 2).hour, 2 * 3.6082746666700003)
    assert abs((a1 / 3.123456).hour - 3.60827466667 / 3.123456) < 1e-10

    # commutativity
    assert (2 * a1).hour == (a1 * 2).hour

    a3 = Angle(a1)  # makes a *copy* of the object, but identical content as a1
    assert_allclose(a1.radian, a3.radian)
    assert a1 is not a3

    a4 = abs(-a1)
    assert a4.radian == a1.radian

    a5 = Angle(5.0, unit=u.hour)
    assert a5 > a1
    assert a5 >= a1
    assert a1 < a5
    assert a1 <= a5


def test_angle_convert():
    """
    Test unit conversion of Angle objects
    """
    angle = Angle("54.12412", unit=u.degree)

    assert_allclose(angle.hour, 3.60827466667)
    assert_allclose(angle.radian, 0.944644098745)
    assert_allclose(angle.degree, 54.12412)

    assert len(angle.hms) == 3
    assert isinstance(angle.hms, tuple)
    assert angle.hms[0] == 3
    assert angle.hms[1] == 36
    assert_allclose(angle.hms[2], 29.78879999999947)
    #also check that the namedtuple attribute-style access works:
    assert angle.hms.h == 3
    assert angle.hms.m == 36
    assert_allclose(angle.hms.s, 29.78879999999947)

    assert len(angle.dms) == 3
    assert isinstance(angle.dms, tuple)
    assert angle.dms[0] == 54
    assert angle.dms[1] == 7
    assert_allclose(angle.dms[2], 26.831999999992036)
    #also check that the namedtuple attribute-style access works:
    assert angle.dms.d == 54
    assert angle.dms.m == 7
    assert_allclose(angle.dms.s, 26.831999999992036)

    assert isinstance(angle.dms[0], float)
    assert isinstance(angle.hms[0], float)

    #now make sure dms and signed_dms work right for negative angles
    negangle = Angle("-54.12412", unit=u.degree)

    assert negangle.dms.d == -54
    assert negangle.dms.m == -7
    assert_allclose(negangle.dms.s, -26.831999999992036)
    assert negangle.signed_dms.sign == -1
    assert negangle.signed_dms.d == 54
    assert negangle.signed_dms.m == 7
    assert_allclose(negangle.signed_dms.s, 26.831999999992036)


def test_angle_formatting():
    """
    Tests string formatting for Angle objects
    """

    '''
    The string method of Angle has this signature:
    def string(self, unit=DEGREE, decimal=False, sep=" ", precision=5,
               pad=False):

    The "decimal" parameter defaults to False since if you need to print the
    Angle as a decimal, there's no need to use the "format" method (see
    above).
    '''

    angle = Angle("54.12412", unit=u.degree)

    #__str__ is the default `format`
    assert str(angle) == angle.to_string()

    res = 'Angle as HMS: 3h36m29.7888s'
    assert "Angle as HMS: {0}".format(angle.to_string(unit=u.hour)) == res

    res = 'Angle as HMS: 3:36:29.7888'
    assert "Angle as HMS: {0}".format(angle.to_string(unit=u.hour, sep=":")) == res

    res = 'Angle as HMS: 3:36:29.79'
    assert "Angle as HMS: {0}".format(angle.to_string(unit=u.hour, sep=":",
                                      precision=2)) == res

    # Note that you can provide one, two, or three separators passed as a
    # tuple or list

    res = 'Angle as HMS: 3h36m29.7888s'
    assert "Angle as HMS: {0}".format(angle.to_string(unit=u.hour,
                                                   sep=("h", "m", "s"),
                                                   precision=4)) == res

    res = 'Angle as HMS: 3-36|29.7888'
    assert "Angle as HMS: {0}".format(angle.to_string(unit=u.hour, sep=["-", "|"],
                                                   precision=4)) == res

    res = 'Angle as HMS: 3-36-29.7888'
    assert "Angle as HMS: {0}".format(angle.to_string(unit=u.hour, sep="-",
                                                    precision=4)) == res

    res = 'Angle as HMS: 03h36m29.7888s'
    assert "Angle as HMS: {0}".format(angle.to_string(unit=u.hour, precision=4,
                                                  pad=True)) == res

    # Same as above, in degrees

    angle = Angle("3 36 29.78880", unit=u.degree)

    res = 'Angle as DMS: 3d36m29.7888s'
    assert "Angle as DMS: {0}".format(angle.to_string(unit=u.degree)) == res

    res = 'Angle as DMS: 3:36:29.7888'
    assert "Angle as DMS: {0}".format(angle.to_string(unit=u.degree, sep=":")) == res

    res = 'Angle as DMS: 3:36:29.79'
    assert "Angle as DMS: {0}".format(angle.to_string(unit=u.degree, sep=":",
                                      precision=2)) == res

    # Note that you can provide one, two, or three separators passed as a
    # tuple or list

    res = 'Angle as DMS: 3d36m29.7888s'
    assert "Angle as DMS: {0}".format(angle.to_string(unit=u.degree,
                                                   sep=("d", "m", "s"),
                                                   precision=4)) == res

    res = 'Angle as DMS: 3-36|29.7888'
    assert "Angle as DMS: {0}".format(angle.to_string(unit=u.degree, sep=["-", "|"],
                                                   precision=4)) == res

    res = 'Angle as DMS: 3-36-29.7888'
    assert "Angle as DMS: {0}".format(angle.to_string(unit=u.degree, sep="-",
                                                    precision=4)) == res

    res = 'Angle as DMS: 03d36m29.7888s'
    assert "Angle as DMS: {0}".format(angle.to_string(unit=u.degree, precision=4,
                                                  pad=True)) == res

    res = 'Angle as rad: 0.0629763rad'
    assert "Angle as rad: {0}".format(angle.to_string(unit=u.radian)) == res

    res = 'Angle as rad decimal: 0.0629763'
    assert "Angle as rad decimal: {0}".format(angle.to_string(unit=u.radian, decimal=True)) == res


    # check negative angles

    angle = Angle(-1.23456789, unit=u.degree)
    angle2 = Angle(-1.23456789, unit=u.hour)

    assert angle.to_string() == '-1d14m04.4444s'
    assert angle.to_string(pad=True) == '-01d14m04.4444s'
    assert angle.to_string(unit=u.hour) == '-0h04m56.2963s'
    assert angle2.to_string(unit=u.hour, pad=True) == '-01h14m04.4444s'
    assert angle.to_string(unit=u.radian, decimal=True) == '-0.0215473'

def test_angle_format_roundtripping():
    """
    Ensures that the string represtation of an angle can be used to create a
    new valid Angle.
    """

    a1 = Angle(0, unit=u.radian)
    a2 = Angle(10, unit=u.degree)
    a3 = Angle(0.543, unit=u.degree)
    a4 = Angle('1d2m3.4s')

    assert Angle(str(a1)).degree == a1.degree
    assert Angle(str(a2)).degree == a2.degree
    assert Angle(str(a3)).degree == a3.degree
    assert Angle(str(a4)).degree == a4.degree

    #also check Longitude/Latitude
    ra = Longitude('1h2m3.4s')
    dec = Latitude('1d2m3.4s')

    assert_allclose(Angle(str(ra)).degree, ra.degree)
    assert_allclose(Angle(str(dec)).degree, dec.degree)


def test_radec():
    """
    Tests creation/operations of Longitude and Latitude objects
    """

    '''
    Longitude and Latitude are objects that are subclassed from Angle. As with Angle, Longitude
    and Latitude can parse any unambiguous format (tuples, formatted strings, etc.).

    The intention is not to create an Angle subclass for every possible
    coordinate object (e.g. galactic l, galactic b). However, equatorial Longitude/Latitude
    are so prevalent in astronomy that it's worth creating ones for these
    units. They will be noted as "special" in the docs and use of the just the
    Angle class is to be used for other coordinate systems.
    '''

    with pytest.raises(u.UnitsError):
        ra = Longitude("4:08:15.162342")  # error - hours or degrees?
    with pytest.raises(u.UnitsError):
        ra = Longitude("-4:08:15.162342")

    # the "smart" initializer allows >24 to automatically do degrees, but the
    #Angle-based one does not
    #TODO: adjust in 0.3 for whatever behavior is decided on

    #ra = Longitude("26:34:15.345634")  # unambiguous b/c hours don't go past 24
    #assert_allclose(ra.degree, 26.570929342)
    with pytest.raises(u.UnitsError):
        ra = Longitude("26:34:15.345634")

    #ra = Longitude(68)
    with pytest.raises(u.UnitsError):
        ra = Longitude(68)

    with pytest.raises(u.UnitsError):
        ra = Longitude(12)

    with pytest.raises(ValueError):
        ra = Longitude("garbage containing a d and no units")

    ra = Longitude("12h43m23s")
    assert_allclose(ra.hour, 12.7230555556)

    ra = Longitude((56, 14, 52.52), unit=u.degree)      # can accept tuples
    #TODO: again, fix based on >24 behavior
    #ra = Longitude((56,14,52.52))
    with pytest.raises(u.UnitsError):
        ra = Longitude((56, 14, 52.52))
    with pytest.raises(u.UnitsError):
        ra = Longitude((12, 14, 52))  # ambiguous w/o units
    ra = Longitude((12, 14, 52), unit=u.hour)

    ra = Longitude([56, 64, 52.2], unit=u.degree)  # ...but not arrays (yet)

    # Units can be specified
    ra = Longitude("4:08:15.162342", unit=u.hour)

    #TODO: this was the "smart" initializer behavior - adjust in 0.3 appropriately
    ## Where Longitude values are commonly found in hours or degrees, declination is
    ## nearly always specified in degrees, so this is the default.
    #dec = Latitude("-41:08:15.162342")
    with pytest.raises(u.UnitsError):
        dec = Latitude("-41:08:15.162342")
    dec = Latitude("-41:08:15.162342", unit=u.degree)  # same as above


def test_negative_zero_dms():
    # Test for DMS parser
    a = Angle('-00:00:10', u.deg)
    assert_allclose(a.degree, -10. / 3600.)

    # Unicode minus
    a = Angle('−00:00:10', u.deg)
    assert_allclose(a.degree, -10. / 3600.)


def test_negative_zero_dm():
    # Test for DM parser
    a = Angle('-00:10', u.deg)
    assert_allclose(a.degree, -10. / 60.)


def test_negative_zero_hms():
    # Test for HMS parser
    a = Angle('-00:00:10', u.hour)
    assert_allclose(a.hour, -10. / 3600.)


def test_negative_zero_hm():
    # Test for HM parser
    a = Angle('-00:10', u.hour)
    assert_allclose(a.hour, -10. / 60.)


def test_negative_sixty_hm():
    # Test for HM parser
    a = Angle('-00:60', u.hour)
    assert_allclose(a.hour, -1.)


def test_plus_sixty_hm():
    # Test for HM parser
    a = Angle('00:60', u.hour)
    assert_allclose(a.hour, 1.)


def test_negative_fifty_nine_sixty_dms():
    # Test for DMS parser
    a = Angle('-00:59:60', u.deg)
    assert_allclose(a.degree, -1.)


def test_plus_fifty_nine_sixty_dms():
    # Test for DMS parser
    a = Angle('+00:59:60', u.deg)
    assert_allclose(a.degree, 1.)


def test_negative_sixty_dms():
    # Test for DMS parser
    a = Angle('-00:00:60', u.deg)
    assert_allclose(a.degree, -1. / 60.)


def test_plus_sixty_dms():
    # Test for DMS parser
    a = Angle('+00:00:60', u.deg)
    assert_allclose(a.degree, 1. / 60.)


def test_angle_to_is_angle():
    a = Angle('00:00:60', u.deg)
    assert isinstance(a, Angle)
    assert isinstance(a.to(u.rad), Angle)


def test_angle_to_quantity():
    a = Angle('00:00:60', u.deg)
    q = u.Quantity(a)
    assert isinstance(q, u.Quantity)
    assert q.unit is u.deg


def test_quantity_to_angle():
    a = Angle(1.0*u.deg)
    assert isinstance(a, Angle)
    with pytest.raises(u.UnitsError):
        Angle(1.0*u.meter)
    a = Angle(1.0*u.hour)
    assert isinstance(a, Angle)
    assert a.unit is u.hourangle
    with pytest.raises(u.UnitsError):
        Angle(1.0*u.min)


def test_angle_string():
    a = Angle('00:00:60', u.deg)
    assert str(a) == '0d01m00s'
    a = Angle('-00:00:10', u.hour)
    assert str(a) == '-0h00m10s'
    a = Angle(3.2, u.radian)
    assert str(a) == '3.2rad'
    a = Angle(4.2, u.microarcsecond)
    assert str(a) == '4.2uarcsec'
    a = Angle('1.0uarcsec')
    assert a.value == 1.0
    assert a.unit == u.microarcsecond
    a = Angle("3d")
    assert_allclose(a.value, 3.0)
    assert a.unit == u.degree
    a = Angle('10"')
    assert_allclose(a.value, 10.0)
    assert a.unit == u.arcsecond
    a = Angle("10'")
    assert_allclose(a.value, 10.0)
    assert a.unit == u.arcminute


def test_angle_repr():
    assert 'Angle' in repr(Angle(0, u.deg))
    assert 'Longitude' in repr(Longitude(0, u.deg))
    assert 'Latitude' in repr(Latitude(0, u.deg))

    a = Angle(0, u.deg)
    repr(a)


def test_large_angle_representation():
    """Test that angles above 360 degrees can be output as strings,
    in repr, str, and to_string.  (regression test for #1413)"""
    a = Angle(350, u.deg) + Angle(350, u.deg)
    a.to_string()
    a.to_string(u.hourangle)
    repr(a)
    repr(a.to(u.hourangle))
    str(a)
    str(a.to(u.hourangle))


def test_wrap_at_inplace():
    a = Angle([-20, 150, 350, 360] * u.deg)
    out = a.wrap_at('180d', inplace=True)
    assert out is None
    assert np.all(a.degree == np.array([-20., 150., -10., 0.]))


def test_latitude():
    with pytest.raises(ValueError):
        lat = Latitude(['91d', '89d'])
    with pytest.raises(ValueError):
        lat = Latitude('-91d')

    lat = Latitude(['90d', '89d'])
    # check that one can get items
    assert lat[0] == 90 * u.deg
    assert lat[1] == 89 * u.deg
    # and that comparison with angles works
    assert np.all(lat == Angle(['90d', '89d']))
    # check setitem works
    lat[1] = 45. * u.deg
    assert np.all(lat == Angle(['90d', '45d']))
    # but not with values out of range
    with pytest.raises(ValueError):
        lat[0] = 90.001 * u.deg
    with pytest.raises(ValueError):
        lat[0] = -90.001 * u.deg
    # these should also not destroy input (#1851)
    assert np.all(lat == Angle(['90d', '45d']))

    # conserve type on unit change (closes #1423)
    angle = lat.to('radian')
    assert type(angle) is Latitude
    # but not on calculations
    angle = lat - 190 * u.deg
    assert type(angle) is Angle
    assert angle[0] == -100 * u.deg

    lat = Latitude('80d')
    angle = lat / 2.
    assert type(angle) is Angle
    assert angle == 40 * u.deg

    angle = lat * 2.
    assert type(angle) is Angle
    assert angle == 160 * u.deg

    angle = -lat
    assert type(angle) is Angle
    assert angle == -80 * u.deg


def test_longitude():
    # Default wrapping at 360d with an array input
    lon = Longitude(['370d', '88d'])
    assert np.all(lon == Longitude(['10d', '88d']))
    assert np.all(lon == Angle(['10d', '88d']))

    # conserve type on unit change and keep wrap_angle (closes #1423)
    angle = lon.to('hourangle')
    assert type(angle) is Longitude
    assert angle.wrap_angle == lon.wrap_angle
    angle = lon[0]
    assert type(angle) is Longitude
    assert angle.wrap_angle == lon.wrap_angle
    angle = lon[1:]
    assert type(angle) is Longitude
    assert angle.wrap_angle == lon.wrap_angle

    # but not on calculations
    angle = lon / 2.
    assert np.all(angle == Angle(['5d', '44d']))
    assert type(angle) is Angle
    assert not hasattr(angle, 'wrap_angle')

    angle = lon * 2. + 400 * u.deg
    assert np.all(angle == Angle(['420d', '576d']))
    assert type(angle) is Angle

    # Test setting a mutable value and having it wrap
    lon[1] = -10 * u.deg
    assert np.all(lon == Angle(['10d', '350d']))

    # Test wrapping and try hitting some edge cases
    lon = Longitude(np.array([0, 0.5, 1.0, 1.5, 2.0]) * np.pi, unit=u.radian)
    assert np.all(lon.degree == np.array([0., 90, 180, 270, 0]))

    lon = Longitude(np.array([0, 0.5, 1.0, 1.5, 2.0]) * np.pi, unit=u.radian, wrap_angle='180d')
    assert np.all(lon.degree == np.array([0., 90, -180, -90, 0]))

    # Wrap on setting wrap_angle property (also test auto-conversion of wrap_angle to an Angle)
    lon = Longitude(np.array([0, 0.5, 1.0, 1.5, 2.0]) * np.pi, unit=u.radian)
    lon.wrap_angle = '180d'
    assert np.all(lon.degree == np.array([0., 90, -180, -90, 0]))

    lon = Longitude('460d')
    assert lon == Angle('100d')
    lon.wrap_angle = '90d'
    assert lon == Angle('-260d')

    #check for problem reported in #2037 about Longitude initializing to -0
    lon = Longitude(0, u.deg)
    lonstr = lon.to_string()
    assert not lonstr.startswith('-')

    #also make sure dtype is correctly conserved
    assert Longitude(0, u.deg, dtype=float).dtype == np.dtype(float)
    assert Longitude(0, u.deg, dtype=int).dtype == np.dtype(int)



def test_wrap_at():
    a = Angle([-20, 150, 350, 360] * u.deg)
    assert np.all(a.wrap_at(360 * u.deg).degree == np.array([340., 150., 350., 0.]))
    assert np.all(a.wrap_at(Angle(360, unit=u.deg)).degree == np.array([340., 150., 350., 0.]))
    assert np.all(a.wrap_at('360d').degree == np.array([340., 150., 350., 0.]))
    assert np.all(a.wrap_at('180d').degree == np.array([-20., 150., -10., 0.]))
    assert np.all(a.wrap_at(np.pi * u.rad).degree == np.array([-20., 150., -10., 0.]))

    # Test wrapping a scalar Angle
    a = Angle('190d')
    assert a.wrap_at('180d') == Angle('-170d')

    a = Angle(np.arange(-1000.0, 1000.0, 0.125), unit=u.deg)
    for wrap_angle in (270, 0.2, 0.0, 360.0, 500, -2000.125):
        aw = a.wrap_at(wrap_angle * u.deg)
        assert np.all(aw.degree >= wrap_angle - 360.0)
        assert np.all(aw.degree < wrap_angle)

        aw = a.to(u.rad).wrap_at(wrap_angle * u.deg)
        assert np.all(aw.degree >= wrap_angle - 360.0)
        assert np.all(aw.degree < wrap_angle)


def test_is_within_bounds():
    a = Angle([-20, 150, 350] * u.deg)
    assert a.is_within_bounds('0d', '360d') is False
    assert a.is_within_bounds(None, '360d') is True
    assert a.is_within_bounds(-30 * u.deg, None) is True

    a = Angle('-20d')
    assert a.is_within_bounds('0d', '360d') is False
    assert a.is_within_bounds(None, '360d') is True
    assert a.is_within_bounds(-30 * u.deg, None) is True


def test_angle_mismatched_unit():
    a = Angle('+6h7m8s', unit=u.degree)
    assert_allclose(a.value, 91.78333333333332)


def test_regression_formatting_negative():
    # Regression test for a bug that caused:
    #
    # >>> Angle(-1., unit='deg').to_string()
    # '-1d00m-0s'
    assert Angle(-0., unit='deg').to_string() == '-0d00m00s'
    assert Angle(-1., unit='deg').to_string() == '-1d00m00s'
    assert Angle(-0., unit='hour').to_string() == '-0h00m00s'
    assert Angle(-1., unit='hour').to_string() == '-1h00m00s'

def test_empty_sep():
    a = Angle('05h04m31.93830s')

    assert a.to_string(sep='', precision=2, pad=True) == '050431.94'

def test_create_tuple():
    """
    Tests creation of an angle with a (d,m,s) or (h,m,s) tuple
    """
    a1 = Angle((1, 30, 0), unit=u.degree)
    assert a1.value == 1.5

    a1 = Angle((1, 30, 0), unit=u.hourangle)
    assert a1.value == 1.5

def test_list_of_quantities():
    a1 = Angle([1*u.deg, 1*u.hourangle])
    assert a1.unit == u.deg
    assert_allclose(a1.value, [1, 15])

    a2 = Angle([1*u.hourangle, 1*u.deg], u.deg)
    assert a2.unit == u.deg
    assert_allclose(a2.value, [15, 1])

