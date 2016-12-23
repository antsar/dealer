""" Mercurial support. """

from __future__ import absolute_import

import datetime
from dateutil.tz import tzoffset

from .base import SCMBackend, logger

try:
    from mercurial import ui, hg as HG, error  # noqa

    class Backend(SCMBackend):

        """ Mercurial backend. """

        def init_repo(self):
            """ Initialize repository. """
            try:
                self._repo = HG.repository(ui.ui(), path=self.path or '.')
                self._revision = self._repo[len(self._repo) - 1].hex()
                self._tag = self._repo.tagslist()[0][1]
                hg_date, hg_offset = self._repo[len(self._repo) - 1].date()
                hg_tz = tzoffset(None, hg_offset)
                self._revision_date = datetime.datetime.fromtimestamp(
                    hg_date, hg_tz)
            except error.RepoError:
                message = 'Mercurial repository not found: {0}'.format(
                    self.path)
                if not self.options.get('silent'):
                    logger.error(message)

                raise TypeError(message)

            return self._repo

except ImportError:

    class Backend(SCMBackend):

        """ Warning backend. """

        def init_repo(self):
            """ Process error. """
            message = 'Mercurial is not installed.'
            if not self.options.get('silent'):
                logger.error(message)

            raise TypeError(message)


hg = Backend()
