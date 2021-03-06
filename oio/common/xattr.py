# Copyright (C) 2017 OpenIO SAS, as part of OpenIO SDS
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.

from __future__ import absolute_import
import errno

from oio.common.constants import chunk_xattr_keys, \
    CHUNK_XATTR_CONTENT_FULLPATH_PREFIX, OIO_VERSION


xattr = None
try:
    # try python-pyxattr
    import xattr
except ImportError:
    pass
if xattr:
    try:
        xattr.get_all
    except AttributeError:
        # fallback to pyxattr compat mode
        from xattr import pyxattr_compat as xattr


def read_user_xattr(fd):
    it = {}
    try:
        it = xattr.get_all(fd)
    except IOError as e:
        for err in 'ENOTSUP', 'EOPNOTSUPP':
            if hasattr(errno, err) and e.errno == getattr(errno, err):
                raise e

    meta = {k[5:]: v for k, v in it if k.startswith('user.')}
    return meta


def modify_xattr(fd, new_fullpaths, remove_old_xattr, xattr_to_remove):
    for chunk_id, new_fullpath in new_fullpaths.iteritems():
        xattr.setxattr(
            fd,
            'user.' + CHUNK_XATTR_CONTENT_FULLPATH_PREFIX + chunk_id.upper(),
            new_fullpath)

    for key in xattr_to_remove:
        try:
            xattr.removexattr(fd, 'user.' + key)
        except IOError:
            pass

    if remove_old_xattr:
        for key in ['chunk_id', 'container_id', 'content_path',
                    'content_version', 'content_id']:
            try:
                xattr.removexattr(fd, 'user.' + chunk_xattr_keys[key])
            except IOError:
                pass

    xattr.setxattr(fd, 'user.' + chunk_xattr_keys['oio_version'],
                   OIO_VERSION)
