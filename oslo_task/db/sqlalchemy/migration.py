# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os

from migrate import exceptions as versioning_exceptions
from migrate.versioning import api as versioning_api
from migrate.versioning.repository import Repository
from oslo_log import log as logging
import sqlalchemy

from oslo_task.db.sqlalchemy import api as db_session
from oslo_task import exception
from oslo_task._i18n import _


INIT_VERSION=0
_REPOSITORY=None

LOG = logging.getLogger(__name__)


def get_engine():
    return db_session.get_engine()

def db_sync(version=None):
    if version is not None:
        try:
            version = int(version)
        except ValueError:
            raise exception.OsloTaskException(_("version should be an integer"))

    current_version = db_version()
    repository = _find_migrate_repo()
    if version is None or version > current_version:
        return versioning_api.upgrade(get_engine(),
                repository, version)
    else:
        return versioning_api.downgrade(get_engine(),
                repository, version)

def db_version ():
    repository = _find_migrate_repo()
    try:
        return versioning_api.db_version(get_engine(),
                                         repository)
    except versioning_exceptions.DatabaseNotControlledError as exc:
        meta = sqlalchemy.MetaData()
        engine = get_engine()
        meta.reflect(bind=engine)
        tables = meta.tables
        if len(tables) == 0:
            db_version_control(INIT_VERSION)
            return versioning_api.db_version(
                        get_engine(), repository)
        else:
            LOG.exception(exc)
            # Some pre-Essex DB's may not be version controlled.
            # Require them to upgrade using Essex first.
            raise exception.OsloTaskException(
                _("Upgrade DB using Essex release first."))

def db_version_control(version=None):
    repository = _find_migrate_repo()
    versioning_api.version_control(get_engine(),
                                   repository,
                                   version)
    return version

def _find_migrate_repo():
    """Get the path for the migrate repository."""
    global _REPOSITORY
    rel_path = 'migrate_repo'
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        rel_path)
    assert os.path.exists(path)
    if _REPOSITORY is None:
        _REPOSITORY = Repository(path)
    return _REPOSITORY
